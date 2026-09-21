"""YOLOX-family bird detector, ONNX Runtime, CPU/ANE, fully offline after the
one-time model fetch.

WHY THIS MODEL
  YOLOX (Megvii) is Apache-2.0 for both code and the released COCO weights, so
  nothing here constrains what Geno does with the project. The alternative with
  the best accuracy-per-megabyte -- Ultralytics YOLOv8/YOLO11 -- is AGPL-3.0
  and its pip package is heavy and phones home by default. YOLOX ships official
  static-shape ONNX exports, which is exactly what ONNX Runtime's CoreML
  execution provider wants, so the Apple Neural Engine / GPU path works without
  a conversion step. COCO class 14 is `bird`.

WHY TILED
  These are 24 MP frames (5712x4284). Letterboxing a whole frame into the
  model's 640 px input is an 8.9x downscale: a 30 px bird at the far bank
  becomes 3 px, below the model's finest stride (8). PROTOCOL.md section 5a's
  own formula says the same thing -- px_per_cm = W / (150 * distance_m), so a
  60 cm cormorant at 100 m is ~23 native px. The detector therefore sweeps a
  grid of overlapping native-resolution tiles and merges the results, plus one
  whole-frame pass for birds too large to fit in a tile.

  This is the whole point of the stage. A whole-frame-only sweep reproduces the
  failure mode it exists to fix: silently missing distant birds.

TUNING HONESTY
  `conf` defaults to 0.15, chosen on cost asymmetry -- a distant bird missed by
  the sweep is invisible forever, a false positive costs one glance at a crop --
  and NOT fitted to the logged answers in logs/bird-log.md. Raise it for a
  cleaner working set; lower it before concluding a frame is birdless.
"""
import os, sys, urllib.request
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .base import Detector

BIRD_CLASS = 14          # COCO index of `bird`
NUM_CLASSES = 80

# name -> (input size, sha-less URL, approx MB). Official Megvii release assets.
MODELS = {
    'yolox_nano': (416, 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.onnx', 3.5),
    'yolox_tiny': (416, 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_tiny.onnx', 19.3),
    'yolox_s':    (640, 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.onnx', 34.2),
    'yolox_m':    (640, 'https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_m.onnx', 97.2),
}
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')


def model_path(name, fetch=True):
    """Local path to the .onnx, downloading once if absent. Kept inside the
    project rather than a cache dir on purpose: the Cowork VM's $HOME is
    session-scoped, so a cached model would be re-downloaded every session,
    and 'fully offline' should survive a cold cache."""
    if name not in MODELS:
        raise ValueError(f'unknown detector model {name!r}; have {sorted(MODELS)}')
    p = os.path.join(MODEL_DIR, name + '.onnx')
    if os.path.exists(p): return p
    if not fetch:
        raise FileNotFoundError(f'{p} absent and fetch disabled')
    os.makedirs(MODEL_DIR, exist_ok=True)
    url = MODELS[name][1]
    print(f'fetching {name} (~{MODELS[name][2]:.0f} MB, one time) ...', file=sys.stderr)
    tmp = p + '.part'
    urllib.request.urlretrieve(url, tmp)
    os.replace(tmp, p)
    return p


# ---------------------------------------------------------------- pre / post

def _preproc(pil, size):
    """YOLOX's own preprocessing: resize preserving aspect, paste top-left into
    a 114-filled square, BGR channel order, raw 0-255 floats (no /255, no
    mean/std). Getting any of that wrong yields plausible-looking garbage."""
    from PIL import Image
    W, H = pil.size
    r = min(size / H, size / W)
    nw, nh = max(1, int(W * r)), max(1, int(H * r))
    im = pil.resize((nw, nh), Image.BILINEAR)
    pad = np.full((size, size, 3), 114, dtype=np.uint8)
    pad[:nh, :nw] = np.asarray(im.convert('RGB'), dtype=np.uint8)[:, :, ::-1]
    return np.ascontiguousarray(pad.transpose(2, 0, 1)[None].astype(np.float32)), r


def _decode(out, size, strides=(8, 16, 32)):
    """Undo YOLOX's anchor-free grid encoding: centres are grid-relative,
    sizes are log-space, both in stride units."""
    grids, exp = [], []
    for s in strides:
        n = size // s
        xv, yv = np.meshgrid(np.arange(n), np.arange(n))
        g = np.stack((xv, yv), 2).reshape(1, -1, 2)
        grids.append(g); exp.append(np.full((1, g.shape[1], 1), s))
    grids = np.concatenate(grids, 1); exp = np.concatenate(exp, 1)
    out = out.copy()
    out[..., :2] = (out[..., :2] + grids) * exp
    out[..., 2:4] = np.exp(out[..., 2:4]) * exp
    return out


def _suppress(boxes, scores, iou=0.55, contain=0.80):
    """NMS with an extra containment rule.

    Plain IoU-NMS is not enough for tiled inference: a tile boundary can cut a
    bird in half, and the half-box has low IoU with the whole-box, so both
    survive and one bird is reported twice. `contain` also drops a box whose
    own area is mostly inside a higher-scoring box.
    """
    if len(boxes) == 0: return []
    x1, y1, x2, y2 = boxes.T
    area = np.maximum(0, x2-x1) * np.maximum(0, y2-y1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size:
        i = order[0]; keep.append(i); rest = order[1:]
        if rest.size == 0: break
        xx1 = np.maximum(x1[i], x1[rest]); yy1 = np.maximum(y1[i], y1[rest])
        xx2 = np.minimum(x2[i], x2[rest]); yy2 = np.minimum(y2[i], y2[rest])
        inter = np.maximum(0, xx2-xx1) * np.maximum(0, yy2-yy1)
        union = area[i] + area[rest] - inter
        iou_v = inter / np.maximum(union, 1e-9)
        ios_v = inter / np.maximum(area[rest], 1e-9)     # fraction of the smaller box swallowed
        order = rest[(iou_v <= iou) & (ios_v <= contain)]
    return keep


class YOLOXDetector(Detector):
    name = 'yolox'

    def __init__(self, model='yolox_s', conf=0.15, iou=0.55, contain=0.80,
                 tile=1200, overlap=0.25, whole_frame=True, providers=None,
                 max_box_frac=0.9, fetch=True):
        self.model_name = model
        self.size = MODELS[model][0]
        self.conf, self.iou, self.contain = conf, iou, contain
        self.tile, self.overlap = tile, overlap
        self.whole_frame = whole_frame
        self.max_box_frac = max_box_frac
        self.path = model_path(model, fetch=fetch)
        import onnxruntime as ort
        avail = ort.get_available_providers()
        want = providers or ['CoreMLExecutionProvider', 'CPUExecutionProvider']
        self.providers = [p for p in want if p in avail] or ['CPUExecutionProvider']
        so = ort.SessionOptions()
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        try:
            self.sess = ort.InferenceSession(self.path, so, providers=self.providers)
        except Exception:
            self.providers = ['CPUExecutionProvider']
            self.sess = ort.InferenceSession(self.path, so, providers=self.providers)
        self.model = f'{model}@{self.size} [{"+".join(p.replace("ExecutionProvider","") for p in self.providers)}]'

    # ------------------------------------------------------------------ core
    def _one(self, pil):
        blob, r = _preproc(pil, self.size)
        raw = self.sess.run(None, {self.sess.get_inputs()[0].name: blob})[0]
        out = _decode(raw, self.size)[0]
        sc = out[:, 4] * out[:, 5 + BIRD_CLASS]
        m = sc > self.conf
        if not m.any():
            return np.zeros((0, 4), np.float32), np.zeros((0,), np.float32)
        b, sc = out[m, :4], sc[m]
        xy = np.stack([b[:,0]-b[:,2]/2, b[:,1]-b[:,3]/2,
                       b[:,0]+b[:,2]/2, b[:,1]+b[:,3]/2], 1) / r
        return xy.astype(np.float32), sc.astype(np.float32)

    def detect(self, image_path):
        """-> list[(x0, y0, x1, y1, score)] in FRACTIONAL coords, per base.Detector."""
        from PIL import Image
        import pillow_heif; pillow_heif.register_heif_opener()
        pil = Image.open(image_path).convert('RGB')
        W, H = pil.size
        bs, ss = [], []

        if self.whole_frame:
            b, s = self._one(pil)
            if len(b): bs.append(b); ss.append(s)

        # tile <= 0 disables the sweep entirely -- whole-frame only. Kept as a
        # supported setting because it is the honest ablation: it is what a
        # detector without this stage's tiling would see, and comparing the two
        # is how you check the sweep is still earning its runtime.
        t = min(self.tile, W, H) if self.tile > 0 else 0
        step = max(1, int(t * (1 - self.overlap))) if t else 1
        xs = sorted({min(x, max(0, W - t)) for x in range(0, W, step)}) if t else []
        ys = sorted({min(y, max(0, H - t)) for y in range(0, H, step)}) if t else []
        self.last_tiles = len(xs) * len(ys) + (1 if self.whole_frame else 0)
        for y0 in ys:
            for x0 in xs:
                b, s = self._one(pil.crop((x0, y0, x0 + t, y0 + t)))
                if len(b):
                    bs.append(b + np.array([x0, y0, x0, y0], np.float32)); ss.append(s)

        if not bs: return []
        B, S = np.concatenate(bs), np.concatenate(ss)
        B[:, 0::2] = B[:, 0::2].clip(0, W); B[:, 1::2] = B[:, 1::2].clip(0, H)
        keep = _suppress(B, S, self.iou, self.contain)
        B, S = B[keep], S[keep]
        # a box covering most of the frame is the model latching onto the scene
        big = ((B[:,2]-B[:,0]) / W > self.max_box_frac) & ((B[:,3]-B[:,1]) / H > self.max_box_frac)
        B, S = B[~big], S[~big]
        order = S.argsort()[::-1]
        return [(float(B[i,0]/W), float(B[i,1]/H), float(B[i,2]/W), float(B[i,3]/H), float(S[i]))
                for i in order]
