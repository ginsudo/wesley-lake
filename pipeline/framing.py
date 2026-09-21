#!/usr/bin/env python3
"""Deciding when two frames show the SAME birds — so a count is not inflated by
re-photographing. PROTOCOL.md §9: "Distinguish 'same photo re-counted' from
'additive new birds.' Ask when unsure."

Three mechanisms, in increasing order of how much they claim:

1. STALE-FIX DETECTION. Fix the data before grouping it. The first frame after
   the phone wakes often carries the last known position, which invents a
   spurious stop. Detected by implied speed, not by distance.

2. ZOOM BURSTS. A wide frame followed seconds later by a zoomed one is the same
   subject, re-framed. This is the strongest signal available, because zooming
   in is a deliberate act ON the thing just photographed.

3. SIGHTING EVENTS. Adjacent stops close in time and space probably show the
   same birds. Physics, not appearance: birds do not teleport, and the
   photographer only walked so far.

None of these is appearance matching. PROTOCOL.md §6 forbids using image
similarity as evidence of a repeat individual, and nothing here does — every
decision is made from timestamps, positions and lens settings. What these
produce is a *candidate* grouping for pass 2 to confirm, never a merge.

    python3 pipeline/framing.py                 # report over the whole archive
    python3 pipeline/framing.py 2026-09-20      # one date
"""
import os, sys, csv, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import track

# --- tunables, and where each number comes from -----------------------------
MAX_WALK_MPS   = 3.0   # brisk walk; above this a fix is stale, not movement
DECISIVE       = 2.0   # ...and the skip must be this much cleaner, or we are
                       # just flagging the innocent neighbour of a bad fix
MIN_JUMP_M     = 25.0  # ...and the jump must be real. Speed alone is a trap: two
                       # frames 1 s apart and 3.8 m apart read as 3.8 m/s, which
                       # is ordinary GPS jitter, not a stale fix. Frames in the
                       # SAME second divide by zero and used to read as infinite.
ZOOM_GAP_S     = 30    # a zoom-in follows its wide shot within seconds
ZOOM_RATIO     = 1.6   # 35mm-equivalent must rise by this much to count
# Fitted to logs/bird-log.md Entry 4, which called the cormorant roost "one
# continuous sighting across several vantage points" spanning stops 2-4:
# 15:03:48-15:09:58 (370 s) over roughly 50 m. Validated by self_check().
EVENT_GAP_S    = 380
EVENT_DIST_M   = 55
# Beyond ~2x the iPhone is upscaling a sensor crop. 26 mm is this phone's main
# wide; 52 mm is 2x, the largest crop the sensor actually resolves 1:1.
BASE_EQ35      = 26
TRUE_CROP_EQ35 = 52


def load(date=None):
    """Rows from analysis/exif-index.csv, with numbers parsed. One date or all."""
    p = os.path.join(ROOT, 'analysis', 'derived', 'exif-index.csv')
    out = collections.defaultdict(list)
    for r in csv.DictReader(open(p)):
        if not r.get('dt'):
            continue
        d = r['dt'][:10].replace(':', '-')
        if date and d != date:
            continue
        for k in ('lat', 'lon', 'focal', 'eq35', 'zoom'):
            r[k] = float(r[k]) if r.get(k) else None
        out[d].append(r)
    for d in out:
        out[d].sort(key=lambda r: r['dt'])
    return out


def _pos(r):
    return (r['lat'], r['lon'])


def _gap(a, b):
    return track.secs(b['dt']) - track.secs(a['dt'])


# --- 1. stale fixes ---------------------------------------------------------

def _violations(gps, max_mps):
    """Interior frames that look like the liar in their own triple, worst first."""
    out = []
    for i in range(1, len(gps) - 1):
        a, b, c = gps[i-1], gps[i], gps[i+1]
        gab, gbc, gac = _gap(a, b), _gap(b, c), _gap(a, c)
        if gac <= 0 or gab <= 0 or gbc <= 0:
            continue                      # same-second frames: speed is undefined
        dab, dbc = track.hav(_pos(a), _pos(b)), track.hav(_pos(b), _pos(c))
        dac = track.hav(_pos(a), _pos(c))
        vab, vbc, vac = dab / gab, dbc / gbc, dac / gac
        # The step that is TOO FAST must also be a real jump. Checking either
        # step would let a 6.8 m wobble through whenever the other step happens
        # to be long and slow.
        fast = [d for v, d in ((vab, dab), (vbc, dbc)) if v > max_mps]
        if not fast or max(fast) < MIN_JUMP_M:
            continue                      # jitter, not a jump
        if vac > max_mps or max(vab, vbc) < DECISIVE * vac:
            continue                      # removing it does not fix anything
        out.append((max(vab, vbc) / max(vac, 0.05), b['file'],
                    f'implies {vab:.1f} and {vbc:.1f} m/s, but skipping it '
                    f'gives {vac:.1f} m/s — stale fix, position unreliable'))
    out.sort(reverse=True)
    return out


def stale_fixes(rows, max_mps=MAX_WALK_MPS):
    """Frames whose GPS implies impossible movement. Returns {file: reason}.

    A stale fix is identified by its NEIGHBOURS, not by its own coordinates:
    if dropping frame B makes the A->C step a normal walking pace, B is the
    liar. Single-frame stops are the usual victims.

    Resolved ITERATIVELY — worst offender first, then recompute. One bad fix
    makes both of its neighbours look fast, so judging every triple against the
    original track condemns the innocent along with the guilty.
    """
    gps = [r for r in rows if r['lat'] is not None]
    bad = {}
    while len(gps) >= 3:
        v = _violations(gps, max_mps)
        if not v:
            break
        _, f, why = v[0]
        bad[f] = why
        gps = [r for r in gps if r['file'] != f]
    # Ends have only one neighbour, so they get the weaker test — and only once
    # the interior is clean, or a bad second frame would condemn the first.
    for i, j in ((0, 1), (len(gps)-1, len(gps)-2)):
        if len(gps) < 3:
            break
        a, b = gps[i], gps[j]
        g = abs(_gap(a, b))
        d = track.hav(_pos(a), _pos(b))
        if g > 0 and d >= MIN_JUMP_M and d / g > max_mps:
            bad.setdefault(a['file'],
                           f'implies {d/g:.1f} m/s against its only neighbour — '
                           f'stale fix likely (first/last of a burst)')
    return bad


# --- 2. zoom bursts ---------------------------------------------------------

def zoom_class(a, b):
    """How much REAL extra detail the zoomed frame b carries over wide frame a.

    The physical focal length is the giveaway: this phone has a 5.96 mm main
    and a 2.22 mm ultrawide and no telephoto, so any rise in 35mm-equivalent
    within one lens is a sensor crop, not optics.
    """
    if a['focal'] and b['focal'] and abs(a['focal'] - b['focal']) > 0.1:
        return 'lens_change', 'different physical lens — genuinely different optics'
    eq = b['eq35'] or 0
    if eq <= TRUE_CROP_EQ35:
        return 'real_crop', (f'{eq}mm-eq is within the sensor 1:1 crop (<={TRUE_CROP_EQ35}mm) '
                             f'— about 1.4x more true pixels on subject')
    return 'interpolated', (f'{eq}mm-eq is ~{eq/BASE_EQ35:.1f}x on a {BASE_EQ35}mm lens with no '
                            f'telephoto — upscaled past the 2x sensor crop. No more information '
                            f'than cropping the wide frame, and PROTOCOL.md §5a applies: the '
                            f'apparent detail is partly synthesised')


def zoom_bursts(rows, gap_s=ZOOM_GAP_S, ratio=ZOOM_RATIO):
    """Runs of frames that re-photograph one subject at increasing zoom.

    Returns a list of lists of filenames, each a burst in time order, wide
    first. A burst is ONE subject: count it once.
    """
    out, cur = [], []
    for a, b in zip(rows, rows[1:]):
        if not (a['eq35'] and b['eq35']):
            cur = []; continue
        g = _gap(a, b)
        if 0 <= g <= gap_s and b['eq35'] >= a['eq35'] * ratio:
            if not cur:
                cur = [a['file']]
            cur.append(b['file'])
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return out


# --- 3. sighting events -----------------------------------------------------

def events(rows, gap_s=EVENT_GAP_S, dist_m=EVENT_DIST_M, drop_stale=True):
    """Group STOPS into sighting events — stretches that may show the same birds.

    Looser than a stop on purpose: a stop is where the photographer stood, an
    event is how long the birds stayed the same birds. Returns a list of lists
    of stops (each stop a list of rows).
    """
    gps = [r for r in rows if r['lat'] is not None]
    if drop_stale:
        bad = stale_fixes(rows)
        gps = [r for r in gps if r['file'] not in bad]
    if not gps:
        return []
    ss = track.stops(gps)
    out, cur = [], [ss[0]]
    for prev, s in zip(ss, ss[1:]):
        g = _gap(prev[-1], s[0])
        d = track.hav(_pos(prev[-1]), _pos(s[0]))
        if g <= gap_s and d <= dist_m:
            cur.append(s)
        else:
            out.append(cur); cur = [s]
    out.append(cur)
    return out


# --- validation against the one date with a known answer --------------------

def self_check(verbose=True):
    """Entry 4 grouped the cormorant roost as ONE sighting across stops 2-4
    (IMG_3458-3477) and treated the east-end raft, the heron and the swans as
    separate. If the parameters above do not reproduce that, they are wrong.
    """
    rows = load('2026-09-20')['2026-09-20']
    ev = events(rows)
    groups = [[r['file'][4:8] for s in e for r in s] for e in ev]
    problems = []
    roost = {f'{n:04d}' for n in range(3458, 3478)}
    hit = [g for g in groups if roost & set(g)]
    if len(hit) != 1:
        problems.append(f'cormorant roost frames split across {len(hit)} events')
    else:
        extra = set(hit[0]) - roost
        if extra:
            problems.append(f'roost event also swallowed {sorted(extra)}')
    if len(stale_fixes(rows)) != 1 or 'IMG_3488.HEIC' not in stale_fixes(rows):
        problems.append(f'stale-fix detector should flag IMG_3488 and only it, '
                        f'got {sorted(stale_fixes(rows))}')
    raft = {f'{n:04d}' for n in range(3449, 3458)}
    if any(raft & set(g) and roost & set(g) for g in groups):
        problems.append('east-end raft merged with the cormorant roost — too loose')
    if verbose:
        print(f'self-check against logs/bird-log.md Entry 4 '
              f'(gap<={EVENT_GAP_S}s, dist<={EVENT_DIST_M}m):')
        for i, g in enumerate(groups, 1):
            print(f'   event {i}: {g[0]}..{g[-1]}  ({len(g)} frames)')
        print('   ' + ('OK — keeps the east-end raft separate, groups the cormorant '
                       'roost as one sighting across 3 stops (Entry 4: "not additive"), '
                       'and flags IMG_3488 alone as stale'
                       if not problems else 'FAILED: ' + '; '.join(problems)))
        print('   note: event 3 merges the heron mat with the Asbury-bank mallards. '
              'That is correct behaviour — events group geometrically and pass 2 '
              'splits them by species.')
    return problems


def assign(rows, **kw):
    """-> (stop_of, event_of), covering EVERY frame including stale-fixed ones.

    `events()` drops frames with a bad GPS fix before clustering, which is right
    -- a stale position must not shape the grouping. But the frame itself is a
    real photograph of real birds, and if it comes back with no event it escapes
    the double-counting guard in census.py entirely (that guard skips records
    whose event is None). So a dropped frame inherits the event and stop of its
    nearest neighbour IN TIME: its timestamp is trustworthy even though its
    position is not.
    """
    gps = [r for r in rows if r['lat'] is not None]
    bad = stale_fixes(rows)
    clean = [r for r in gps if r['file'] not in bad]
    stop_of, event_of = {}, {}
    for i, s in enumerate(track.stops(clean) if clean else [], 1):
        for r in s:
            stop_of[r['file']] = i
    for i, e in enumerate(events(rows, **kw), 1):
        for s in e:
            for r in s:
                event_of[r['file']] = i
    for r in rows:
        if r['file'] in event_of or not clean:
            continue
        near = min(clean, key=lambda c: abs(_gap(c, r)))
        stop_of.setdefault(r['file'], stop_of.get(near['file']))
        event_of[r['file']] = event_of.get(near['file'])
    return stop_of, event_of


def report(date=None):
    for d, rows in sorted(load(date).items()):
        bad = stale_fixes(rows)
        bursts = zoom_bursts(rows)
        ev = events(rows)
        if not (bad or bursts or len(ev) != len(track.stops([r for r in rows if r['lat']]))):
            continue
        print(f'\n[{d}]  {len(rows)} photos')
        for f, why in bad.items():
            print(f'   stale fix  {f[4:8]}: {why}')
        for b in bursts:
            eqs = {r['file']: r['eq35'] for r in rows}
            a = next(r for r in rows if r['file'] == b[0])
            z = next(r for r in rows if r['file'] == b[-1])
            kind, why = zoom_class(a, z)
            chain = ' -> '.join(f"{f[4:8]}({int(eqs[f])}mm)" for f in b)
            print(f'   zoom burst {chain}   [{kind}] — one subject, count once')
            print(f'              {why}')
        ss = track.stops([r for r in rows if r['lat'] is not None])
        if len(ev) < len(ss):
            for i, e in enumerate(ev, 1):
                if len(e) > 1:
                    fl = [r['file'][4:8] for s in e for r in s]
                    print(f'   event {i}: stops merged, {fl[0]}..{fl[-1]} '
                          f'({len(e)} stops, {len(fl)} frames) — may be one sighting')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    self_check()
    report(args[0] if args else None)
