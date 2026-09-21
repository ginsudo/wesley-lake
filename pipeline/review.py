#!/usr/bin/env python3
"""Build the two views pass 2 actually needs, per sighting event.

The 2026-09-19 pilot showed these are different jobs and one view cannot do both:

  COUNTING view  — boxed frames at usable resolution. Counting needs spatial
                   relationships, which crops destroy: you cannot see that two
                   crops are the same bird from two tiles.
  ID view        — a grid of native-resolution crops, biggest score first.
                   Fast for species, useless for counting.

Both are laid out per EVENT, not per frame, because the count is per event:
frames inside one event are re-views of the same birds (PROTOCOL.md §9), and
frames inside a zoom burst certainly are. Each event's header states the peak
single-frame box count — the number pass 2 should start from — rather than the
event total, which is inflated.

    python3 pipeline/review.py 2026-09-19
"""
import os, sys, json, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bootstrap
bootstrap.ensure(['PIL', 'pillow_heif'], ['pillow', 'pillow-heif'])
import framing

CONF = 0.30          # triage floor; below this is reviewed only on empty frames
COUNT_CELL = 1500    # per-frame width in the counting sheet
ID_CELL = 300


def _draw(ax, recs, W, H, conf):
    from PIL import ImageDraw
    d = ImageDraw.Draw(ax)
    for r in recs:
        x0, y0, x1, y1 = r['box']
        c = 'red' if r['score'] >= conf else 'yellow'
        d.rectangle([x0*W-6, y0*H-6, x1*W+6, y1*H+6], outline=c, width=10)
        d.text((x0*W, max(0, y0*H-52)), f"{r['detection_id'][-3:]} {r['score']:.2f}", fill=c)


def build(date, conf=CONF, outdir=None):
    from PIL import Image, ImageDraw
    import pillow_heif; pillow_heif.register_heif_opener()

    cand = os.path.join(ROOT, 'analysis', 'derived', f'{date}-candidates.json')
    if not os.path.exists(cand):
        print(f'no candidates for {date} — run detect.py first'); return
    d = json.load(open(cand))
    outdir = outdir or os.path.join(ROOT, 'work', date, 'review')
    os.makedirs(outdir, exist_ok=True)

    by_frame = collections.defaultdict(list)
    for r in d['records']:
        by_frame[os.path.basename(r['photo'])].append(r)
    events = d.get('framing', {}).get('events') or {}
    if not events:
        rows = framing.load(date).get(date, [])
        events = {str(i): [r['file'] for s in e for r in s]
                  for i, e in enumerate(framing.events(rows), 1)}
    bursts = {tuple(b['frames']): b['gain'] for b in d.get('framing', {}).get('zoom_bursts', [])}
    burst_of = {f: (b, g) for b, g in bursts.items() for f in b}
    stale = d.get('framing', {}).get('stale_fixes', {})

    made = []
    for ev, frames in sorted(events.items(), key=lambda kv: int(kv[0])):
        hits = {f: [r for r in by_frame.get(f, []) if r['score'] >= conf] for f in frames}
        peak_f = max(hits, key=lambda f: len(hits[f])) if hits else None
        peak = len(hits[peak_f]) if peak_f else 0
        total = sum(len(v) for v in hits.values())

        # --- counting view: every frame in the event, boxed, side by side
        ims = []
        for f in frames:
            p = os.path.join(ROOT, 'photos', date, f)
            if not os.path.exists(p): continue
            im = Image.open(p).convert('RGB'); W, H = im.size
            ax = im.copy(); _draw(ax, by_frame.get(f, []), W, H, conf)
            ax.thumbnail((COUNT_CELL, COUNT_CELL))
            ims.append((f, ax, len(hits.get(f, []))))
        if ims:
            cols = min(3, len(ims)); rows = (len(ims)+cols-1)//cols
            cw = max(i.width for _, i, _ in ims); ch = max(i.height for _, i, _ in ims)
            sh = Image.new('RGB', (cols*cw, rows*(ch+34)), 'white'); dr = ImageDraw.Draw(sh)
            for i, (f, im, n) in enumerate(ims):
                x = (i % cols)*cw; y = (i//cols)*(ch+34)
                sh.paste(im, (x, y+30))
                tag = f'{f[4:8]}  {n} boxes'
                if f in burst_of:
                    b, g = burst_of[f]
                    tag += f'   [zoom burst {b[0][4:8]}..{b[-1][4:8]} · {g} · SAME SUBJECT]'
                if f in stale: tag += '   [GPS STALE]'
                dr.text((x+6, y+6), tag, fill='black')
            o = os.path.join(outdir, f'event{int(ev):02d}-count.jpg')
            sh.save(o, quality=86); made.append(o)

        # --- ID view: crops, biggest score first
        crops = sorted([r for f in frames for r in by_frame.get(f, []) if r['score'] >= conf],
                       key=lambda r: -r['score'])[:36]
        if crops:
            cols = 6; rows = (len(crops)+cols-1)//cols
            sh = Image.new('RGB', (cols*ID_CELL, rows*(ID_CELL+22)), 'white')
            dr = ImageDraw.Draw(sh)
            for i, r in enumerate(crops):
                cp = os.path.join(ROOT, r['crop']) if not os.path.isabs(r['crop']) else r['crop']
                if not os.path.exists(cp): continue
                im = Image.open(cp).convert('RGB'); im.thumbnail((ID_CELL-8, ID_CELL-8))
                x = (i % cols)*ID_CELL; y = (i//cols)*(ID_CELL+22)
                sh.paste(im, (x+4, y+18))
                dr.text((x+5, y+3), f"{r['detection_id'][4:]} {r['score']:.2f}", fill='black')
            o = os.path.join(outdir, f'event{int(ev):02d}-id.jpg')
            sh.save(o, quality=90); made.append(o)

        print(f'  event {ev}: {frames[0][4:8]}..{frames[-1][4:8]}  {len(frames)} frames  '
              f'START FROM {peak} (peak in {peak_f[4:8] if peak_f else "-"}), not {total}')
        nb = {f for f in frames if f in burst_of}
        if nb:
            print(f'            zoom bursts inside this event: '
                  f'{", ".join(sorted(f[4:8] for f in nb))} — re-views, not new birds')
    print(f'\n  -> {len(made)} sheets in {os.path.relpath(outdir, ROOT)}')
    return made


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    for d in (args or [os.path.basename(x) for x in
                       sorted(glob.glob(os.path.join(ROOT, 'photos', '2*')))]):
        print(f'[{d}]')
        build(d)
