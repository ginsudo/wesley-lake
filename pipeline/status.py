#!/usr/bin/env python3
"""What is done and what is not, per date. The answer to "where was I?".

The pipeline splits into two halves and it is worth being blunt about which is
which, because the split is the thing that confuses people:

  MACHINE  ingest, EXIF, geofence, stops, contact sheets, detector sweep,
           review sheets, water crops. All deterministic, all re-runnable,
           all done by `run.py`.
  EYES     species, counts, stratum, surface, and every water judgement.
           A photograph does not identify a bird or assess a lake; a person or
           a Claude session looks at the crops and decides. `observe.py` and
           `water.py` turn those decisions into validated records.

`run.py` cannot do the second half and does not pretend to. What it CAN do is
prepare the material and then say plainly what is still waiting, which is what
this module prints.

    python3 pipeline/status.py           # every date
    python3 pipeline/status.py --todo    # only dates with work outstanding
"""
import os, sys, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def dates():
    return sorted(os.path.basename(d) for d in glob.glob(os.path.join(ROOT, 'photos', '2*'))
                  if os.path.isdir(d))


def _n(pattern):
    return len(glob.glob(os.path.join(ROOT, pattern)))


def state(date):
    # derived/ is regenerable, records/ is not — see analysis/README.md
    cand = os.path.join(ROOT, 'analysis', 'derived', f'{date}-candidates.json')
    obs = os.path.join(ROOT, 'analysis', 'records', f'{date}-observations.json')
    wat = os.path.join(ROOT, 'analysis', 'records', f'{date}-water.json')
    st = {
        'date': date,
        'photos': _n(f'photos/{date}/*'),
        'swept': os.path.exists(cand),
        'detections': 0,
        'reviewed': _n(f'work/{date}/review/*') > 0,
        'water_crop': os.path.exists(os.path.join(ROOT, 'work', date, 'water.jpg')),
        'birds': os.path.exists(obs),
        'bird_records': 0,
        'water': os.path.exists(wat),
    }
    if st['swept']:
        try:
            st['detections'] = sum(1 for r in json.load(open(cand))['records']
                                   if r['score'] >= 0.30)
        except Exception:
            pass
    if st['birds']:
        try:
            st['bird_records'] = len(json.load(open(obs))['records'])
        except Exception:
            pass
    return st


def report(todo_only=False):
    rows = [state(d) for d in dates()]
    tick = lambda b: '  ok ' if b else '  -- '
    print(f"{'date':<12}{'photos':>7}{'dets':>6}{'swept':>7}{'review':>8}"
          f"{'birds':>7}{'water':>7}   what is waiting")
    nb = nw = 0
    for s in rows:
        todo = []
        if not s['swept']:
            todo.append('sweep')
        if not s['birds']:
            todo.append('IDENTIFY birds (eyes)'); nb += 1
        if not s['water']:
            todo.append('ASSESS water (eyes)'); nw += 1
        if todo_only and not todo:
            continue
        print(f"{s['date']:<12}{s['photos']:>7}{s['detections']:>6}"
              f"{tick(s['swept'])}{tick(s['reviewed']):>8}"
              f"{tick(s['birds']):>7}{tick(s['water']):>7}   {', '.join(todo)}")
    print(f"\n{len(rows)} dates · {sum(r['photos'] for r in rows)} photos · "
          f"{sum(r['bird_records'] for r in rows)} bird records")
    if nb or nw:
        print(f"WAITING ON EYES: {nb} date(s) need bird identification, "
              f"{nw} need a water assessment.")
        print("  birds: python3 pipeline/review.py <date>   then write records via observe.py")
        print("  water: look at work/<date>/water.jpg       then write a record via water.py")
    else:
        print("Nothing waiting. Every date has been swept, identified and assessed.")
    return rows


if __name__ == '__main__':
    report('--todo' in sys.argv)
