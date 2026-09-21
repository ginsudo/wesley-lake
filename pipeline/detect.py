#!/usr/bin/env python3
"""Detection stage: sweep every frame of a date, crop what is found, and emit
one candidate record per detection.

Optional. `config.json` -> roles.detector == "none" makes this a no-op; nothing
below runs and nothing is written.

What it produces, per date:
    work/<date>/crops/<FRAME>-b<NN>.jpg          the bird, padded for context
    work/<date>/crops/<FRAME>-b<NN>-<zone>.jpg   PROTOCOL.md 5a sub-crops
    work/<date>/overlay/<FRAME>.jpg              boxes drawn on a reduced frame
    analysis/<date>-candidates.json              one record per detection

work/ is disposable and regenerable (CLAUDE.md); analysis/ is not, but the
candidates file is derived and safe to overwrite. Nothing under logs/ or
photos/ is touched.

WHAT THIS STAGE DOES NOT DO
  It does not identify anything. Every record comes out species '', confidence
  'unknown', tier 'D', marks_checked False. A detector box means "something
  bird-shaped is here at native resolution", which is a claim about where to
  look, not about what it is. Pass 2 (PROTOCOL.md section 4) still happens.

  It also does not assign STRATUM or SURFACE, so every record is
  census_class 'undetermined' and contributes to no count. It cannot: telling
  open water from shallows from a mat needs depth and support, and a box has
  neither. What it does instead is lay out the worksheet -- which mats
  geography.md already knows appear in which frames of this date -- so pass 2
  assigns surfaces against evidence rather than memory. See PROTOCOL.md 5b.
"""
import os, sys, json, glob, time, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import bootstrap
bootstrap.ensure(['PIL', 'pillow_heif', 'numpy', 'onnxruntime'],
                 ['pillow', 'pillow-heif', 'numpy', 'onnxruntime'])

import schema, exif, surfaces, framing
from crop import crop_box

# ------------------------------------------------------------------ 5a zones
# Box-relative bands, NOT detected anatomy. A detector box has no orientation,
# so these are "the part of the box where legs usually are", not "the legs".
# PROTOCOL.md 5a wants legs, neck, bill and wing looked at; this puts a
# native-resolution crop of each band in front of whoever does the looking.
ZONES = {
    'head_bill':  (0.00, 0.00, 1.00, 0.38),
    'neck':       (0.00, 0.15, 1.00, 0.62),
    'wing_flank': (0.00, 0.30, 1.00, 0.85),
    'legs_feet':  (0.00, 0.62, 1.00, 1.00),
}

# Below this many native pixels on the long side of the box, sub-crops are not
# worth writing: PROTOCOL.md 5a needs ~3-4 px to SEE a mark, so a band inside a
# ~60 px bird is at best 2-3 px of leg. Recorded in the record either way.
MIN_BOX_PX_FOR_MARKS = 160


def _zone_box(l, t, r, b, zone):
    zl, zt, zr, zb = ZONES[zone]
    w, h = r - l, b - t
    return (l + w*zl, t + h*zt, l + w*zr, t + h*zb)


def _overlay(pil, dets, out, conf_hi=0.30):
    from PIL import Image, ImageDraw
    im = pil.copy(); d = ImageDraw.Draw(im); W, H = im.size
    for i, (l, t, r, b, s) in enumerate(dets, 1):
        c = 'red' if s >= conf_hi else 'yellow'
        d.rectangle([l*W-5, t*H-5, r*W+5, b*H+5], outline=c, width=8)
        d.text((l*W, max(0, t*H-44)), f'b{i:02d} {s:.2f}', fill=c)
    im.thumbnail((1600, 1600))
    im.save(out, quality=86)


def _px_per_cm(width_px, distance_m):
    """PROTOCOL.md 5a. Only meaningful if distance is known; it isn't here, so
    this is used in reverse -- see `implied_distance_m`."""
    return width_px / (150.0 * distance_m)


def is_fresh(date, photo_dir=None, out_json=None):
    """True if the candidates file already covers every photo now on disk.

    run.py promises idempotence -- 'safe to re-run any time', 45 s. Detection
    costs ~1.2 s per 24 MP frame, so re-sweeping all 27 dates on every run
    would quietly break that promise. A date is re-swept only when a photo is
    newer than its candidates file, or the detector settings changed.
    """
    photo_dir = photo_dir or os.path.join(ROOT, 'photos', date)
    out_json = out_json or os.path.join(ROOT, 'analysis', f'{date}-candidates.json')
    if not os.path.exists(out_json): return False
    try:
        prev = json.load(open(out_json))
    except Exception:
        return False
    stamp = os.path.getmtime(out_json)
    photos = [p for p in glob.glob(os.path.join(photo_dir, '*')) if os.path.isfile(p)]
    if prev.get('photos') != len(photos): return False
    return all(os.path.getmtime(p) <= stamp for p in photos)


def settings_of(det):
    return {'provider': det.name, 'model': getattr(det, 'model', ''),
            'conf': getattr(det, 'conf', None), 'iou': getattr(det, 'iou', None),
            'tile': getattr(det, 'tile', None), 'overlap': getattr(det, 'overlap', None),
            'whole_frame': getattr(det, 'whole_frame', None)}


def detect_date(date, det, photo_dir=None, work_dir=None, out_json=None,
                overlays=True, verbose=True):
    from PIL import Image
    import pillow_heif; pillow_heif.register_heif_opener()

    photo_dir = photo_dir or os.path.join(ROOT, 'photos', date)
    work_dir = work_dir or os.path.join(ROOT, 'work', date)
    out_json = out_json or os.path.join(ROOT, 'analysis', f'{date}-candidates.json')
    crops_dir = os.path.join(work_dir, 'crops')
    ov_dir = os.path.join(work_dir, 'overlay')
    os.makedirs(crops_dir, exist_ok=True)
    if overlays: os.makedirs(ov_dir, exist_ok=True)
    os.makedirs(os.path.dirname(out_json), exist_ok=True)

    photos = sorted(p for p in glob.glob(os.path.join(photo_dir, '*'))
                    if os.path.isfile(p) and not os.path.basename(p).startswith('.'))
    try:
        mats_by_frame = surfaces.by_frame(date=date)
    except Exception:
        mats_by_frame = {}

    # Which frames re-photograph which. framing.py decides this from timestamps,
    # positions and lens settings only -- never from what the pictures look
    # like (PROTOCOL.md section 6). See its docstring.
    try:
        frows = framing.load(date).get(date, [])
        stale = framing.stale_fixes(frows)
        # assign() covers stale-fixed frames too — see its docstring. Computing
        # stops and events from different tracks used to leave a stale frame
        # with a stop but no event, and a record with no event slips past the
        # double-counting guard in census.py.
        stop_of, event_of = framing.assign(frows)
        burst_of = {}
        byname = {r['file']: r for r in frows}
        for b in framing.zoom_bursts(frows):
            kind, why = framing.zoom_class(byname[b[0]], byname[b[-1]])
            for j, f in enumerate(b):
                burst_of[f] = {'burst': b, 'role': 'wide' if j == 0 else 'zoomed',
                               'gain': kind, 'why': why}
    except Exception as e:
        print(f'  !! framing unavailable ({e}) — records will carry no stop/event')
        stale, stop_of, event_of, burst_of = {}, {}, {}, {}
    records, n_clean, n_bad, t0 = [], 0, 0, time.time()

    for p in photos:
        base = os.path.splitext(os.path.basename(p))[0]
        dets = det.detect(p)
        pil = Image.open(p).convert('RGB')
        W, H = pil.size
        ex = exif.parse(p)
        if verbose:
            print(f'  {os.path.basename(p):<16} {len(dets):>3} det  '
                  + ' '.join(f'{d[4]:.2f}' for d in dets[:8]))
        if overlays:
            _overlay(pil, dets, os.path.join(ov_dir, base + '.jpg'))

        for i, (l, t, r, b, s) in enumerate(dets, 1):
            tag = f'{base}-b{i:02d}'
            bw_px, bh_px = int((r-l)*W), int((b-t)*H)
            long_px = max(bw_px, bh_px)

            cp = crop_box(pil, os.path.join(crops_dir, tag + '.jpg'), l, t, r, b, pad=0.35)

            subs, why = {}, ''
            if long_px >= MIN_BOX_PX_FOR_MARKS:
                for z in ZONES:
                    zb = _zone_box(l, t, r, b, z)
                    res = crop_box(pil, os.path.join(crops_dir, f'{tag}-{z}.jpg'),
                                   *zb, pad=0.20)
                    if res: subs[z] = os.path.relpath(res[0], ROOT)
            else:
                why = (f'box is {long_px} px on its long side, under the '
                       f'{MIN_BOX_PX_FOR_MARKS} px floor where PROTOCOL.md 5a sub-crops '
                       f'could show a band or deformity; sub-crops not written')

            # Distance the box size implies, via PROTOCOL.md 5a in reverse, for a
            # nominal 60 cm bird. Rough -- it assumes the main wide lens and a
            # side-on bird -- and it is a sanity aid, not a measurement.
            implied = round((W / 150.0) * (60.0 / max(long_px, 1)), 1)

            bznote = ''
            _bz = burst_of.get(os.path.basename(p))
            if _bz:
                bznote = (f" RE-PHOTOGRAPHED: this frame is the {_bz['role']} member of a "
                          f"zoom burst {_bz['burst'][0]}..{_bz['burst'][-1]} — one subject. "
                          f"{_bz['why']}.")
            rec = schema.blank(
                os.path.relpath(p, ROOT),
                provider=det.name, model=getattr(det, 'model', ''),
                count=1, count_exact=False,
                notes=('detector box only — nothing identified. '
                       + (why if why else 'sub-crops written for the 5a hard-mark check.')
                       + bznote),
            )
            fr = os.path.basename(p)
            bz = burst_of.get(fr)
            rec.update(
                detection_id=tag,
                stop=stop_of.get(fr), event=event_of.get(fr),
                frames=[fr],
                # A detector box is one box in one frame. Whether it is a NEW
                # bird is pass 2's call -- but the grouping below tells pass 2
                # exactly which other frames it has to look at first.
                count_basis='single_frame',
                zoom_burst=(bz['burst'] if bz else None),
                zoom_role=(bz['role'] if bz else None),
                zoom_gain=(bz['gain'] if bz else None),
                gps_suspect=(stale.get(fr) or None),
                # PROTOCOL.md 5b. Left undetermined on purpose -- see the module
                # docstring. Candidate mats are the ones geography.md records as
                # visible in THIS frame; a frame can show two, and a box carries
                # no depth, so this narrows the choice, it does not make it.
                surface_candidates=mats_by_frame.get(base.split('_')[-1], []),
                box=[round(v, 6) for v in (l, t, r, b)],
                box_px=[bw_px, bh_px],
                score=round(s, 4),
                crop=os.path.relpath(cp[0], ROOT) if cp else None,
                crop_px=list(cp[1]) if cp else None,
                subcrops=subs,
                marks_resolvable=bool(subs),
                implied_distance_m=implied,
                frame_px=[W, H],
                lat=ex.get('lat'), lon=ex.get('lon'), dt=ex.get('dt'),
            )
            probs = schema.validate(rec)
            if probs:
                rec['problems'] = probs      # written, never dropped
                n_bad += 1
            else:
                n_clean += 1
            records.append(rec)

    payload = {
        'date': date,
        'generated': datetime.datetime.now().isoformat(timespec='seconds'),
        'detector': settings_of(det),
        'photos': len(photos),
        'detections': len(records),
        'validated_clean': n_clean,
        'validation_problems': n_bad,
        'framing': {
            'stale_fixes': stale,
            'zoom_bursts': [{'frames': b, 'gain': framing.zoom_class(
                                byname[b[0]], byname[b[-1]])[0]}
                            for b in framing.zoom_bursts(frows)] if frows else [],
            'events': {str(i): [r['file'] for s_ in e for r in s_]
                       for i, e in enumerate(framing.events(frows), 1)} if frows else {},
            'note': ('Detections are NOT deduplicated across frames. Frames sharing an '
                     'event, and especially frames in one zoom burst, are re-views of the '
                     'same birds — summing them inflates the count ~2.8x. PROTOCOL.md 9.'),
        },
        'surfaces': {
            'assignable': surfaces.assignable(),
            'mats_known_in_these_frames': {
                f: m for f, m in sorted(mats_by_frame.items())
                if any(f in os.path.basename(p) for p in photos)},
            'note': ('PROTOCOL.md 5b. Every record here is census_class '
                     '"undetermined" — the detector assigns no stratum, so nothing '
                     'in this file counts toward the core count yet. Pass 2 sets '
                     'stratum and surface; census class then follows from stratum.'),
        },
        'caveat': ('A detection is a place to look, not an identification. '
                   'Species, age, stratum, activity and tier are all unset; '
                   'PROTOCOL.md section 4 pass 2 still has to happen on the crops.'),
        'records': records,
    }
    with open(out_json, 'w') as f:
        json.dump(payload, f, indent=1)
    if verbose:
        print(f'  -> {len(records)} detections over {len(photos)} photos in '
              f'{time.time()-t0:.0f}s; {n_clean} clean, {n_bad} with problems')
        print(f'  -> {os.path.relpath(out_json, ROOT)}')
    return payload


def settings_changed(date, det, out_json=None):
    out_json = out_json or os.path.join(ROOT, 'analysis', f'{date}-candidates.json')
    if not os.path.exists(out_json): return True
    try:
        return json.load(open(out_json)).get('detector') != settings_of(det)
    except Exception:
        return True


def dates_on_disk():
    return sorted(os.path.basename(d) for d in glob.glob(os.path.join(ROOT, 'photos', '2*'))
                  if os.path.isdir(d))


def main(argv):
    from providers import get, config
    det = get('detector')
    if det is None:
        print('detector: none — stage skipped'); return 0
    force = '--force' in argv or '-f' in argv
    only = [a for a in argv if not a.startswith('-')]
    todo = only or dates_on_disk()
    print(f'detector: {det.name} / {getattr(det, "model", "")}')
    for d in todo:
        if not force and is_fresh(d) and not settings_changed(d, det):
            print(f'[{d}] up to date — skipping (--force to re-sweep)'); continue
        print(f'[{d}]')
        detect_date(d, det)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
