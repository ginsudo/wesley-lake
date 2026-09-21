#!/usr/bin/env python3
"""Water-quality observations — what a photograph can honestly support, and
nothing beyond it. PROTOCOL.md §3a.

WHY THIS IS SEPARATE FROM schema.py
  A water observation is per-PLACE-per-VISIT, not per-bird. Bolting these fields
  onto the bird record would put a lake-condition claim on every mallard.

WHAT THIS DELIBERATELY DOES NOT MEASURE
  Colour, clarity and turbidity are absent on purpose. A patch of Wesley Lake
  sampled across the year reads RGB 185,181,169 in sun and 89,95,96 in shade --
  the variance is illumination, and iPhone HDR and auto white balance sit on top
  of that. Depth is not visible in a photograph, so clarity cannot be read from
  one either. A number derived from those pixels would be invented precision,
  which PROTOCOL.md §9 forbids. If clarity ever matters, it needs a Secchi disk,
  not a better algorithm.

  Algae is absent too, for a different reason: there is none anywhere in the
  262-photograph archive, so there is nothing to calibrate a scale against. A
  bloom would be obvious and goes in `notable` until there is enough to define
  categories from.

THE QUALITY FLAG MATTERS
  `surface_state` is not data about the lake. It records whether the frame
  supports assessment at all -- wind-whipped water hides floating litter. When
  it is `wind_whipped` or `not_assessable`, validate() insists the counts say so.

    python3 pipeline/water.py            # stations, vocabularies, the record so far
    python3 pipeline/water.py --prepare  # build work/<date>/water.jpg for every date
"""
import os, re, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import surfaces                      # for the shared geography.md table parser

NA = 'not_assessable'

# Every vocabulary carries NA, which means what "not visible" means in a feature
# string (§5a): a real answer, distinct from a zero.
SURFACE_STATE  = ['glassy', 'rippled', 'wind_whipped', 'frozen', NA]

# Added after the 2026-09-21 exhaustive sweep, which overturned an earlier
# conclusion. Sampling RGB from a fixed crop box showed illumination dominating
# (the same patch read 185 in sun, 89 in shade) and colour was ruled out. That
# was the wrong test. Looking at all 262 frames by eye shows the water is
# sometimes unmistakably ochre-brown and sometimes grey-blue -- and a reflective
# surface UNDER A CLEAR BLUE SKY would look blue, so brown under blue sky is the
# water's own colour, not a reflection. It is judged, never measured, and only
# under a sky that makes the judgement possible.
SKY            = ['clear', 'mixed', 'overcast', NA]
WATER_APPEARANCE = ['brown_opaque', 'olive_green', 'grey_neutral',
                    'blue_reflective', NA]
ICE_COVER      = ['none', 'partial', 'complete', NA]
# Revised on first contact with real data: the 2026-09-21 frame shows a dense
# band across the lower mesh that is neither "light" nor up to the rail, and the
# first vocabulary had no value for it. Categories written before seeing the
# thing they describe are usually wrong once.
ORGANIC_LOAD   = ['clear', 'scattered', 'banded_below_rail', 'packed_to_rail',
                  'overtopping', NA]
WATER_LEVEL    = ['below_sill', 'at_sill', 'mid_posts', 'at_rail', 'above_rail', NA]
MARGINAL_VEG   = ['absent', 'sparse', 'fringing', 'dense', NA]
LITTER_TYPES   = ['plastic_film', 'bottle_can', 'other']

# Counting litter through water that is not flat is guesswork.
_HIDES_LITTER = ('wind_whipped', NA, 'frozen')


def stations(path=None):
    """-> {id: {where, why, gives}} from geography.md. Places live there, not here."""
    path = path or os.path.join(ROOT, 'geography.md')
    with open(path) as f:
        text = f.read()
    out = {}
    for header, rows in surfaces._tables(text, '## Water-quality stations'):
        for c in rows:
            m = re.search(r'(?:WQ-[0-9A-Za-z]+|LAKE-WIDE)', c[0])
            if not m:
                continue
            out[m.group(0)] = {
                'where': surfaces._pick(header, c, 'where'),
                'why':   surfaces._pick(header, c, 'why'),
                'gives': surfaces._pick(header, c, 'gives', 'what it'),
            }
    return out


def blank(date, station, **kw):
    r = dict(date=date, station=station, frames=None,
             sky=NA, water_appearance=NA,
             surface_state=NA, ice_cover=NA, organic_load=NA,
             water_level=NA, marginal_vegetation=NA,
             litter_count=None, litter_exact=False, litter_range=None,
             litter_types=[], notable='', notes='',
             provider='', model='')
    r.update(kw)
    return r


LAKE_WIDE = 'LAKE-WIDE'   # not a place; see geography.md


def validate(r, known=None):
    """Return a list of problems. Empty list = clean. Never silently coerce."""
    p = []
    known = stations() if known is None else known
    # A roving observation has no fixed framing, so nothing local is comparable.
    # Ice is the exception: it is a whole-lake property you can see from anywhere.
    if r.get('station') == LAKE_WIDE:
        for f in ('organic_load', 'water_level', 'marginal_vegetation'):
            if r.get(f) != NA:
                p.append(f"station LAKE-WIDE but {f}={r.get(f)!r} — without a fixed "
                         f"station that is not comparable to anything; use "
                         f"{NA!r} or record it at a station")
        if r.get('litter_count') is not None:
            p.append("station LAKE-WIDE with a litter_count — a count with no fixed "
                     "framing cannot be compared between visits")
    if r.get('station') not in known:
        p.append(f"unknown station {r.get('station')!r}; "
                 f"geography.md has {sorted(known)}")
    if not r.get('frames'):
        p.append("no frames — a water observation must cite the photographs it is read from")
    elif not isinstance(r['frames'], list):
        p.append("frames must be a list")
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(r.get('date') or '')):
        p.append(f"bad date {r.get('date')!r}")

    for field, vocab in (('sky', SKY), ('water_appearance', WATER_APPEARANCE),
                         ('surface_state', SURFACE_STATE), ('ice_cover', ICE_COVER),
                         ('organic_load', ORGANIC_LOAD), ('water_level', WATER_LEVEL),
                         ('marginal_vegetation', MARGINAL_VEG)):
        if r.get(field) not in vocab:
            p.append(f"bad {field} {r.get(field)!r}; one of {vocab}")

    # Colour is only judgeable when the sky would betray a reflection.
    if r.get('water_appearance') != NA and r.get('sky') != 'clear':
        p.append(f"water_appearance {r.get('water_appearance')!r} with sky "
                 f"{r.get('sky')!r} — colour is only judgeable under a CLEAR sky, "
                 f"where a merely reflective surface would look blue")

    # Colour is only judgeable when the sky would betray a reflection.
    if r.get('water_appearance') != NA and r.get('sky') != 'clear':
        p.append(f"water_appearance {r.get('water_appearance')!r} with sky "
                 f"{r.get('sky')!r} — colour is only judgeable under a CLEAR sky, "
                 f"where a merely reflective surface would look blue")

    n = r.get('litter_count')
    if n is not None:
        if not isinstance(n, int) or n < 0:
            p.append(f"litter_count must be a non-negative integer, got {n!r}")
        # A count through disturbed water is not a count.
        elif r.get('surface_state') in _HIDES_LITTER and r.get('litter_exact'):
            p.append(f"litter_exact with surface_state {r['surface_state']!r} — "
                     "floating litter cannot be counted exactly through that surface")
    lr = r.get('litter_range')
    if lr is not None:
        if not (isinstance(lr, (list, tuple)) and len(lr) == 2
                and all(isinstance(x, int) for x in lr)):
            p.append(f"litter_range must be [low, high] integers, got {lr!r}")
        elif lr[0] > lr[1]:
            p.append(f"litter_range {lr!r} is inverted")
        elif n is not None and not (lr[0] <= n <= lr[1]):
            p.append(f"litter_count {n} is outside its own litter_range {lr!r}")
        elif r.get('litter_exact'):
            p.append("litter_exact is True but a litter_range is given — pick one")
    bad = [t for t in (r.get('litter_types') or []) if t not in LITTER_TYPES]
    if bad:
        p.append(f"unknown litter_types {bad}; one of {LITTER_TYPES}")
    if (r.get('litter_types') and not n) or (n and not r.get('litter_types')):
        p.append("litter_count and litter_types must be given together")

    # Ice and surface state have to agree with each other.
    if r.get('ice_cover') == 'complete' and r.get('surface_state') not in ('frozen', NA):
        p.append(f"ice_cover 'complete' but surface_state {r.get('surface_state')!r}")
    if r.get('surface_state') == 'frozen' and r.get('ice_cover') in ('none',):
        p.append("surface_state 'frozen' but ice_cover 'none'")
    return p


def prepare(date, out=None):
    """Build work/<date>/water.jpg — every frame of the date cropped to its water
    band, which is what the 2026-09-21 exhaustive sweep used to find a dumped
    drum, a floating carcass and green surface patches that a bird-focused
    review had missed.

    This is the MACHINE half of a water observation: the pipeline prepares the
    material, a person judges it. Nothing here decides anything.
    """
    from PIL import Image, ImageDraw
    import pillow_heif; pillow_heif.register_heif_opener()
    import glob as _glob
    paths = sorted(p for p in _glob.glob(os.path.join(ROOT, 'photos', date, '*'))
                   if os.path.isfile(p) and not os.path.basename(p).startswith('.'))
    if not paths:
        return None
    out = out or os.path.join(ROOT, 'work', date, 'water.jpg')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cell, cols = 760, 5
    ims = []
    for p_ in paths:
        im = Image.open(p_).convert('RGB'); W, H = im.size
        c = im.crop((0, int(0.34*H), W, int(0.88*H)))      # the water band
        c.thumbnail((cell, cell))
        ims.append((os.path.basename(p_)[4:8], c))
    rows = (len(ims) + cols - 1)//cols
    cw = max(i.width for _, i in ims); ch = max(i.height for _, i in ims)
    sh = Image.new('RGB', (min(cols, len(ims))*cw, rows*(ch+22)), 'white')
    dr = ImageDraw.Draw(sh)
    for i, (t, c) in enumerate(ims):
        x = (i % cols)*cw; y = (i//cols)*(ch+22)
        sh.paste(c, (x, y+18)); dr.text((x+3, y+3), t, fill='black')
    sh.save(out, quality=88)
    return out


def process(records, date, path=None):
    path = path or os.path.join(ROOT, 'analysis', f'{date}-water.json')
    known = stations()
    bad = 0
    for r in records:
        pr = validate(r, known)
        if pr:
            r['problems'] = pr; bad += 1
        else:
            r.pop('problems', None)
    payload = {
        'date': date,
        'generated': datetime.datetime.now().isoformat(timespec='seconds'),
        'schema': 'pipeline/water.py — PROTOCOL.md §3a',
        'caveat': ('Categories only. No colour, clarity or turbidity: illumination '
                   'dominates the pixels and depth is not visible in a photograph. '
                   'Counts are of what is VISIBLE, which is a lower bound.'),
        'records': records,
        'validation_problems': bad,
    }
    with open(path, 'w') as f:
        json.dump(payload, f, indent=1)
    return payload, bad


def report(paths=None):
    paths = paths or sorted(__import__('glob').glob(
        os.path.join(ROOT, 'analysis', '*-water.json')))
    if not paths:
        print('no water observations yet'); return
    print(f"{'date':<12}{'stn':<11}{'surface':<14}{'ice':<9}{'organic':<20}"
          f"{'level':<12}{'litter':>7}")
    for p in paths:
        for r in json.load(open(p))['records']:
            n = r.get('litter_count')
            lr = r.get('litter_range')
            lit = '—' if n is None else (f'{lr[0]}–{lr[1]}' if lr else str(n))
            print(f"{r['date']:<12}{r['station']:<11}{r['surface_state']:<14}"
                  f"{r['ice_cover']:<9}{r['organic_load']:<20}{r['water_level']:<12}{lit:>7}")
            if r.get('notable'): print(f"{'':<12}  notable: {r['notable']}")
            if r.get('problems'): print(f"{'':<12}  PROBLEMS: {r['problems']}")


if __name__ == '__main__':
    if '--prepare' in sys.argv:
        import glob as _g
        for d in sorted(os.path.basename(x) for x in
                        _g.glob(os.path.join(ROOT, 'photos', '2*'))):
            o = prepare(d)
            if o: print('  ', os.path.relpath(o, ROOT))
        sys.exit(0)
    st = stations()
    print(f'{len(st)} station(s) in geography.md:')
    for k, v in st.items():
        print(f'  {k}  {v["where"][:88]}')
    print('\nvocabularies:')
    for name, v in (('surface_state', SURFACE_STATE), ('ice_cover', ICE_COVER),
                    ('organic_load', ORGANIC_LOAD), ('water_level', WATER_LEVEL),
                    ('marginal_vegetation', MARGINAL_VEG), ('litter_types', LITTER_TYPES)):
        print(f'  {name:<22}{v}')
    print()
    report()


save = process   # observe.py calls its writer process(); keep one verb for both
