#!/usr/bin/env python3
"""Roll a set of observation records up into the lake's numbers.

PROTOCOL.md 5b: the core count is birds ON THE LAKE SURFACE -- floating, standing
in the water, or on a floating mat. Everything else is noted and reported
separately, never folded in.

    python3 pipeline/census.py analysis/2026-09-20-candidates.json

Works on any file holding schema.py records: a candidates file from the detector,
or a hand-written pass-2 file. Records the detector produced carry no stratum, so
they land in `undetermined` and are counted toward NOTHING -- that is the honest
answer, and this tool says so loudly rather than quietly reporting zero.
"""
import os, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import schema, surfaces


def load(path):
    with open(path) as f:
        d = json.load(f)
    return d.get('records', d) if isinstance(d, dict) else d


def tally(records):
    out_dups = []
    out = {
        'core': 0, 'noted': 0, 'undetermined': 0, 'core_hi': 0, 'noted_hi': 0,
        'by_surface': collections.Counter(),
        'by_stratum': collections.Counter(),
        'core_species': collections.Counter(),
        'by_segment': collections.Counter(),
        'noted_species': collections.Counter(),
        'problems': [],
        'not_summed': out_dups,
    }
    # PROTOCOL.md section 9. Two records of one species in one sighting event are
    # the same birds re-photographed unless one says `additive`. Sum them and the
    # count inflates ~2.8x from re-photographing alone (measured over the archive).
    seen = collections.defaultdict(list)
    for r in records:
        # Keyed on STRATUM and AGE CLASS as well as species and event, because
        # both are reasons two records are genuinely different birds rather than
        # one group re-photographed:
        #   mallards on the bank vs mallards on the water -- split on purpose,
        #     since 5b counts one and not the other;
        #   an adult swan vs its cygnets -- same species, same water, additive.
        # Without them the split record is silently swallowed and the count reads
        # low (or, for the bank/water case, zero).
        key = (r.get('species') or '', r.get('event'), r.get('stratum') or '',
               r.get('age_class') or '')
        if key[1] is not None and r.get('count_basis') != 'additive':
            seen[key].append(r)
    dup_ids = set()
    for (sp, ev, _st, _ag), rs in seen.items():
        if len(rs) > 1:
            keep = max(rs, key=lambda r: r.get('count') or 0)
            for r in rs:
                if r is not keep:
                    dup_ids.add(id(r))
                    out_dups.append(f"{sp or '(unidentified)'} in event {ev}: "
                                    f"{r.get('detection_id') or r.get('photo')} not summed — "
                                    f"same species, same event, not marked additive")

    for r in records:
        if id(r) in dup_ids:
            continue
        # `or 1` here used to turn count=0 into 1, so a deliberately recorded
        # no-bird observation ("MAT-02 empty", "flat calm, nothing on the lake")
        # counted as one bird. 0 is a real count and the whole point of those
        # records; only a MISSING count defaults to 1.
        n = r['count'] if r.get('count') is not None else 1
        # A logged range like "5-6" stays a range all the way to the total.
        # PROTOCOL.md 9: never upgrade an estimate into an exact number.
        cr = r.get('count_range')
        hi = cr[1] if isinstance(cr, (list, tuple)) and len(cr) == 2 \
                      and isinstance(cr[1], (int, float)) else n
        out['core_hi'] = out.get('core_hi', 0); out['noted_hi'] = out.get('noted_hi', 0)
        st = r.get('stratum') or ''
        cc = r.get('census_class') or 'undetermined'
        # Trust stratum over a stated census_class; validate() reports the clash.
        derived = schema.census_of(st)
        if st and derived != cc:
            out['problems'].append(
                f"{r.get('detection_id') or r.get('photo')}: census_class {cc!r} "
                f"vs stratum {st!r} implying {derived!r}")
            cc = derived
        out[cc] += n
        if cc == 'core': out['core_hi'] += hi
        elif cc == 'noted': out['noted_hi'] += hi
        if st: out['by_stratum'][st] += n
        sp = r.get('species') or '(unidentified)'
        # A count of 0 is a real observation ("this mat held nothing") but it is
        # not a sighting OF anything, so it must not create a species row.
        if cc == 'core':
            if n: out['by_surface'][r.get('surface') or '(surface not named)'] += n
            if n: out['core_species'][sp] += n
            # PROTOCOL.md 8 asks for segment use; every record already carries it.
            if n: out['by_segment'][(r.get('segment') or '?', sp)] += n
        elif cc == 'noted' and n:
            out['noted_species'][sp] += n
        if r.get('species') and r.get('event') is None:
            out['problems'].append(
                f"{r.get('detection_id') or r.get('photo')}: no event — this record "
                "cannot be checked against re-photographing (PROTOCOL.md 9)")
        for pr in schema.validate(r):
            out['problems'].append(f"{r.get('detection_id') or r.get('photo')}: {pr}")
    return out


def report(path):
    recs = load(path)
    t = tally(recs)
    print(f"\n{os.path.basename(path)} — {len(recs)} records\n")
    rng = lambda lo, hi: f'{lo}' if lo == hi else f'{lo}–{hi}'
    print(f"  CORE COUNT (on the lake surface) : {rng(t['core'], t.get('core_hi', t['core']))}")
    print(f"  noted (flying / bank / perch)    : {rng(t['noted'], t.get('noted_hi', t['noted']))}")
    if t['undetermined']:
        print(f"  undetermined                     : {t['undetermined']}"
              "   <- no stratum assigned; counts toward nothing")

    if t['core']:
        print('\n  by surface')
        known = set(surfaces.mat_ids())
        for s, n in t['by_surface'].most_common():
            print(f"    {s:<22} {n}")
        # An empty mat is data (PROTOCOL.md 5b) -- name the ones that held nothing.
        empty = [m for m in known if m != surfaces.UNASSIGNED_MAT
                 and m not in t['by_surface']]
        if empty:
            print(f"    {'— no birds recorded:':<22} {', '.join(sorted(empty))}")
        print('\n  core species')
        for s, n in t['core_species'].most_common():
            print(f"    {s:<22} {n}")
    if t['noted']:
        print('\n  noted species (NOT in the core count)')
        for s, n in t['noted_species'].most_common():
            print(f"    {s:<22} {n}")
    if t['by_segment']:
        print('\n  by segment (core only)')
        seg = collections.defaultdict(list)
        for (g, sp), n in t['by_segment'].most_common():
            seg[g].append(f'{sp} {n}')
        for g in sorted(seg):
            print(f"    {g:<6} {', '.join(seg[g])}")
    if t['by_stratum']:
        print('\n  by stratum')
        for s, n in t['by_stratum'].most_common():
            print(f"    {s:<22} {n}  ({schema.census_of(s)})")
    if t['not_summed']:
        print(f"\n  {len(t['not_summed'])} record(s) NOT summed — re-photographed, "
              f"not additive (PROTOCOL.md 9)")
        for x in t['not_summed'][:10]:
            print(f"    · {x}")
    if t['problems']:
        print(f"\n  {len(t['problems'])} problem(s) — reported, never silently fixed")
        for pr in t['problems'][:20]:
            print(f"    ! {pr}")
        if len(t['problems']) > 20:
            print(f"    ... and {len(t['problems'])-20} more")
    print()
    return t


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    for a in sys.argv[1:]:
        report(a)
