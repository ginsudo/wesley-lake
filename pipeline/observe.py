#!/usr/bin/env python3
"""Pass-2 records: the bridge between what the detector found and what the log says.

The detector produces `analysis/<date>-candidates.json` -- boxes, no meaning.
A human (or a Claude session) looks at the crops and decides what the birds are.
This module is where that decision becomes a validated record.

WHY IT EXISTS
  Those records were being hand-written as ad-hoc dicts, and the metadata that
  is NOT a judgement -- which sighting event a frame belongs to, which stop,
  whether the frames cited even exist -- was being typed out alongside the parts
  that are. Typed metadata is wrong metadata eventually: a bulk backfill once set
  `event: 1` on nine records spanning five different events. It changed no count
  that time, purely by luck, because the records happened to differ in species or
  stratum. Derive it instead.

WHAT IS DERIVED vs WHAT YOU MUST SAY
  derived : stop, event (from framing.py), detections_in_frames (provenance),
            census_class (from stratum, PROTOCOL.md 5b)
  yours   : species, confidence, count, count_basis, age_class, stratum,
            surface, activity, tier, features, marks -- every judgement

PROVENANCE is frame-level, not box-level: `detections_in_frames` lists every
detection in the frames a record cites, so you can get from "Mute Swan 4" back to
the crops it was read from. It does NOT claim those boxes ARE the four swans --
a record can cover a frame that also holds a gull.

    python3 pipeline/observe.py --check          # re-derive and verify everything
    python3 pipeline/observe.py --check --write   # ...and save the corrections
"""
import os, sys, json, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import schema, framing

_EXIF = {}
CONF = 0.30      # provenance floor; matches the review triage in review.py


def _frames_on_disk(date):
    return {os.path.basename(p) for p in glob.glob(os.path.join(ROOT, 'photos', date, '*'))
            if os.path.isfile(p)}


def _detections(date, conf=CONF):
    p = os.path.join(ROOT, 'analysis', f'{date}-candidates.json')
    if not os.path.exists(p):
        return {}
    out = {}
    for r in json.load(open(p))['records']:
        if r['score'] >= conf:
            out.setdefault(os.path.basename(r['photo']), []).append(r['detection_id'])
    return out


def derive(date, record, eo=None, so=None, dets=None, disk=None):
    """Fill in the machine-knowable fields. Returns (record, [problems])."""
    if eo is None or so is None:
        rows = framing.load(date).get(date, [])
        so, eo = framing.assign(rows) if rows else ({}, {})
    dets = _detections(date) if dets is None else dets
    disk = _frames_on_disk(date) if disk is None else disk

    r = dict(record)
    probs = []
    fr = r.get('frames') or []
    if not fr:
        fr = [os.path.basename(r['photo'])]
        r['frames'] = fr

    ghost = [f for f in fr if f not in disk]
    if ghost:
        probs.append(f'frames not on disk: {ghost}')
    real = [f for f in fr if f in disk]

    evs = sorted({eo[f] for f in real if eo.get(f) is not None})
    if len(evs) > 1:
        # Not an error: a record may legitimately span events if the observer
        # judged it one sighting. But it must be said, not implied.
        probs.append(f'frames span sighting events {evs} — if that is deliberate, '
                     f'the count_basis should say so; otherwise split the record')
        r['event'] = evs[0]
    elif evs:
        r['event'] = evs[0]
    stops = sorted({so[f] for f in real if so.get(f) is not None})
    r['stop'] = stops[0] if stops else None

    r['detections_in_frames'] = sorted({d for f in real for d in dets.get(f, [])})
    r['census_class'] = schema.census_of(r.get('stratum'))

    # Segment is derived too -- from the longitudes of the frames the record
    # cites, against the three real crossings (lake.SEGMENTS). It used to be
    # typed, against a scheme bounded by photo-inferred crossings that did not
    # reach the lake's eastern end.
    import lake, csv as _csv
    lons = []
    if _EXIF.get('_loaded') is None:
        _EXIF['_loaded'] = {x['file']: x for x in _csv.DictReader(
            open(os.path.join(ROOT, 'analysis', 'exif-index.csv')))}
    for f in real:
        e = _EXIF['_loaded'].get(f)
        if e and e.get('lon'):
            lons.append(float(e['lon']))
    if lons:
        segs = sorted({lake.segment_for(x) for x in lons} - {''})
        r['segment'] = segs[0] if len(segs) == 1 else (
            '/'.join(segs) if segs else '')
        if len(segs) > 1:
            probs.append(f"frames span segments {segs} — split the record or say so")
    return r, probs


def process(date, records, source='', write=True):
    rows = framing.load(date).get(date, [])
    so, eo = framing.assign(rows) if rows else ({}, {})
    dets, disk = _detections(date), _frames_on_disk(date)
    out, nbad = [], 0
    for rec in records:
        r, probs = derive(date, rec, eo, so, dets, disk)
        probs += schema.validate(r)
        if probs:
            r['problems'] = probs; nbad += 1
        else:
            r.pop('problems', None)
        out.append(r)
    payload = {
        'date': date,
        'generated': datetime.datetime.now().isoformat(timespec='seconds'),
        'source': source or ('Pass 2. Species and counts are Claude’s read of '
                             'native-resolution crops, not Geno’s confirmation '
                             '(PROTOCOL.md 9). Not in logs/bird-log.md.'),
        'derived_by': 'pipeline/observe.py — stop, event, census_class and '
                      'detections_in_frames are computed, not typed',
        'records': out,
        'validation_problems': nbad,
    }
    p = os.path.join(ROOT, 'analysis', f'{date}-observations.json')
    if write:
        json.dump(payload, open(p, 'w'), indent=1)
    return payload, nbad


def recheck(write=False):
    """Re-derive every existing observations file and report what changes."""
    files = sorted(glob.glob(os.path.join(ROOT, 'analysis', '*-observations.json')))
    tot = changed = bad = 0
    for f in files:
        d = json.load(open(f))
        date = d['date']
        rows = framing.load(date).get(date, [])
        so, eo = framing.assign(rows) if rows else ({}, {})
        dets, disk = _detections(date), _frames_on_disk(date)
        diffs = []
        newrecs = []
        for rec in d['records']:
            r, probs = derive(date, rec, eo, so, dets, disk)
            probs += schema.validate(r)
            if probs:
                r['problems'] = probs; bad += 1
            else:
                r.pop('problems', None)
            for k in ('event', 'stop', 'census_class', 'segment'):
                if rec.get(k) != r.get(k):
                    diffs.append(f"{r.get('species') or '(unid)'}: {k} "
                                 f"{rec.get(k)!r} -> {r.get(k)!r}")
            if not rec.get('detections_in_frames') and r['detections_in_frames']:
                diffs.append(f"{r.get('species') or '(unid)'}: +{len(r['detections_in_frames'])} "
                             f"detection ids")
            newrecs.append(r); tot += 1
        if diffs:
            changed += 1
            print(f'[{date}]')
            for x in diffs: print(f'   {x}')
        if write:
            d['records'] = newrecs
            d['validation_problems'] = sum(1 for r in newrecs if r.get('problems'))
            d['derived_by'] = ('pipeline/observe.py — stop, event, census_class and '
                               'detections_in_frames are computed, not typed')
            json.dump(d, open(f, 'w'), indent=1)
    print(f'\n{tot} records across {len(files)} files; {changed} files changed; '
          f'{bad} records with problems' + ('  (written)' if write else '  (dry run)'))
    return bad


if __name__ == '__main__':
    if '--check' in sys.argv:
        sys.exit(1 if recheck('--write' in sys.argv) else 0)
    print(__doc__)
