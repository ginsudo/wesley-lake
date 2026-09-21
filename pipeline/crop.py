"""Pass 2: crop a region at NATIVE resolution for identification.
Usage: crop.py IMG.HEIC out.jpg left top right bottom   (fractions 0-1)
Resolution on subject (iPhone main wide, frame width ~= 1.5 x distance):
  px_per_cm = image_width_px / (150 * distance_m)
  ~3-4 px to SEE a mark; ~15-20 px of character height to READ a band code."""
import sys
from PIL import Image
import pillow_heif
pillow_heif.register_heif_opener()

MAX_SIDE = 1700   # cap: a crop bigger than this is downsampled for viewing
UPSCALE_BELOW = 900  # a crop smaller than this gets ONE 2x pass. Not a floor:
                     # a 40x30 crop comes out 80x60, not 900. That is deliberate.
                     # Enlarging a 40 px bird to 900 px would manufacture exactly
                     # the "pattern read out of a 4-pixel smudge" PROTOCOL.md 5a
                     # forbids. The crop stays as small as the evidence is.

def fit(c):
    """The viewing policy, unchanged since the first version of this file.
    The 2x upscale adds NO information -- it only makes a small native crop
    legible on screen. PROTOCOL.md section 5a: do not read a pattern out of a
    4-pixel smudge just because it has been enlarged."""
    if max(c.size) > MAX_SIDE: c.thumbnail((MAX_SIDE, MAX_SIDE))
    elif max(c.size) < UPSCALE_BELOW: c = c.resize((c.width*2, c.height*2), Image.LANCZOS)
    return c

def crop_box(src, out, l, t, r, b, pad=0.0):
    """Crop fractional box (l,t,r,b) out of `src` at native resolution.

    src  -- path, or an already-open PIL Image (pass the open image when
            cropping many boxes from one photo; decoding a 24 MP HEIC costs
            far more than the crop does).
    pad  -- context margin as a fraction of box size, added on every side and
            clamped to the frame. pad=0 reproduces the original behaviour.

    Returns (out, size) or None if the box is degenerate.
    """
    im = src if hasattr(src, 'crop') else Image.open(src)
    W, H = im.size
    if pad:
        dw, dh = (r-l)*pad, (b-t)*pad
        l, t, r, b = l-dw, t-dh, r+dw, b+dh
    x0, y0 = max(0, int(l*W)), max(0, int(t*H))
    x1, y1 = min(W, int(r*W)), min(H, int(b*H))
    if x1 - x0 < 2 or y1 - y0 < 2: return None
    c = fit(im.crop((x0, y0, x1, y1)))
    c.save(out, quality=95)
    return out, c.size

if __name__ == '__main__':
    src, out, l, t, r, b = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:7])
    res = crop_box(src, out, l, t, r, b)
    print(out, res[1] if res else 'degenerate box')
