#!/usr/bin/env python3
"""Wesley Lake — one-command local processing. Run after dropping a Google Photos
zip in the project root:   python3 pipeline/run.py

Does every deterministic step: unzip, EXIF, geofence, file by date, cluster into
stops, build contact sheets, write a session report. Idempotent — safe to re-run;
with no new zip it just rebuilds derived products from photos/ already on disk.
"""
import os, sys, csv, glob, shutil, zipfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# Deps may live in a session-scoped home that does not persist, and on native
# macOS Homebrew's python refuses installs outright (PEP 668). bootstrap.ensure
# handles both; it may re-exec this script once, into a venv. See bootstrap.py
# and ENVIRONMENT in ../CLAUDE.md.
import bootstrap
bootstrap.ensure(['PIL', 'pillow_heif'], ['pillow', 'pillow-heif'])

import exif, track
from sheets import sheet

# Geofence — PROTOCOL.md 3. Measured from the lake's actual outline (lake.py)
# rather than from a bounding box built out of where Geno happened to stand.
# That box had to be widened twice; this does not.
#
# The buffers are generous on purpose. They absorb two things at once: the real
# bank margin (photographs are taken from banks and bridges, never from the
# water) and a known disagreement between the supplied outline and the archive.
# See lake.LATITUDE_CONFLICT.
import lake

def zone(la, lo):
    return lake.zone(la, lo)

def ingest():
    zips = [z for z in glob.glob(os.path.join(ROOT, '*.zip'))]
    if not zips:
        print('no new zip at root — rebuilding from photos/ on disk'); return 0
    staged = os.path.join(ROOT, 'staging'); os.makedirs(staged, exist_ok=True)
    n = 0
    for z in zips:
        print('unzipping', os.path.basename(z))
        with zipfile.ZipFile(z) as f: f.extractall(staged)
        for p in glob.glob(os.path.join(staged, '**', '*'), recursive=True):
            if not os.path.isfile(p): continue
            r = exif.parse(p)
            if not r.get('dt'):
                print('  !! no datetime, left in staging:', os.path.basename(p)); continue
            d = r['dt'][:10].replace(':', '-')
            sub = 'photos' if zone(r['lat'], r['lon']) != 'OFF' else 'photos/_off-lake'
            dest = os.path.join(ROOT, sub, d); os.makedirs(dest, exist_ok=True)
            dst = os.path.join(dest, os.path.basename(p))
            if not os.path.exists(dst): shutil.move(p, dst); n += 1
        arc = os.path.join(ROOT, 'archive', 'zips'); os.makedirs(arc, exist_ok=True)
        stamp = datetime.date.today().isoformat()
        shutil.move(z, os.path.join(arc, f'{stamp}-{os.path.basename(z)}'))
    print(f'filed {n} photos')
    return n

def build():
    rows = []
    for d in sorted(glob.glob(os.path.join(ROOT, 'photos', '2*'))):
        for p in sorted(glob.glob(os.path.join(d, '*'))):
            if os.path.isfile(p): rows.append(exif.parse(p))
    rows = [r for r in rows if r.get('dt')]
    csvp = os.path.join(ROOT, 'analysis', 'exif-index.csv')
    os.makedirs(os.path.dirname(csvp), exist_ok=True)
    with open(csvp, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['file','dt','tz','model','lat','lon','alt','dir','w','h',
                                          'focal','eq35','zoom','lens'],
                           extrasaction='ignore')
        w.writeheader(); w.writerows(rows)
    print('wrote', csvp, len(rows), 'rows')

    bydate = {}
    for r in rows: bydate.setdefault(r['dt'][:10].replace(':', '-'), []).append(r)
    lines = ['# Wesley Lake — session index', '',
             f'Generated {datetime.datetime.now().isoformat(timespec="seconds")}', '',
             '| date | photos | time range | stops | zones |', '|---|---|---|---|---|']
    for d in sorted(bydate):
        rs = sorted(bydate[d], key=lambda r: r['dt'])
        z = {}
        for r in rs: z[zone(r['lat'], r['lon'])] = z.get(zone(r['lat'], r['lon']), 0) + 1
        gps = [r for r in rs if r['lat']]
        ss = track.stops(gps) if gps else []
        lines.append(f"| {d} | {len(rs)} | {rs[0]['dt'][11:]}–{rs[-1]['dt'][11:]} | {len(ss)} | "
                     + ' '.join(f'{k}:{v}' for k, v in sorted(z.items())) + ' |')
        # contact sheets, one per stop
        wd = os.path.join(ROOT, 'work', d); os.makedirs(wd, exist_ok=True)
        for i, s in enumerate(ss, 1):
            out = os.path.join(wd, f'stop{i}.jpg')
            if os.path.exists(out): continue
            paths = [os.path.join(ROOT, 'photos', d, r['file']) for r in s]
            paths = [p for p in paths if os.path.exists(p)]
            if paths: sheet(paths, out)
    rp = os.path.join(ROOT, 'analysis', 'session-index.md')
    open(rp, 'w').write('\n'.join(lines) + '\n')
    print('wrote', rp)

def detect_stage(dates=None):
    """Optional. config.json roles.detector == "none" -> clean no-op.

    Deliberately last: everything above is deterministic and must not depend on
    a model being configured, and a detector failure must not cost the ingest.
    """
    from providers import get
    try:
        det = get('detector')
    except Exception as e:
        print(f'detector: could not load ({e}) — skipping'); return
    if det is None:
        return
    import detect
    print(f'\ndetector: {det.name} / {getattr(det, "model", "")}')
    for d in (dates or detect.dates_on_disk()):
        if detect.is_fresh(d) and not detect.settings_changed(d, det):
            continue      # keeps run.py cheap and idempotent as documented
        print(f'[{d}]')
        try:
            detect.detect_date(d, det)
        except Exception as e:
            print(f'  !! detection failed on {d}: {e}')

def water_stage(dates=None):
    """Prepare the water-band sheet for each date. PROTOCOL.md §3a.

    The pipeline CANNOT assess water, any more than it can identify a bird —
    both are judgements. What it does is build the material to judge from:
    every frame cropped to its water band, one sheet per date. That is the view
    the 2026-09-21 exhaustive sweep used to find a dumped drum, a floating
    carcass and green surface patches that a bird-focused review had missed.
    """
    import water
    made = 0
    for d in (dates or sorted(os.path.basename(x) for x in
                              glob.glob(os.path.join(ROOT, 'photos', '2*')))):
        out = os.path.join(ROOT, 'work', d, 'water.jpg')
        if os.path.exists(out):
            continue                       # idempotent, like everything above
        try:
            if water.prepare(d): made += 1
        except Exception as e:
            print(f'  !! water sheet failed on {d}: {e}')
    if made:
        print(f'water: built {made} sheet(s) at work/<date>/water.jpg')


if __name__ == '__main__':
    ingest()
    build()
    detect_stage()      # birds:  machine sweep
    water_stage()       # water:  machine prep
    print()
    import status       # then say plainly what still needs eyes
    status.report(todo_only=True)
