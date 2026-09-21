#!/usr/bin/env python3
"""The lake's own shape, and distance to it.

PROTOCOL.md 3 has always used a bounding box built from the observed extent of
walks -- i.e. from where Geno happened to stand. That box has been widened twice,
each time after a confirmed on-lake photo fell outside it, because it described
his habits rather than the water.

This module replaces it with an actual outline. The geofence becomes "how far is
this photo from the water", which is a question about the lake instead of about
the photographer.

    python3 pipeline/lake.py          # outline stats and how the archive sits against it
"""
import math, os, sys

# Wesley Lake perimeter, clockwise from the western head (Railroad Ave) along the
# Asbury Park shore, round the east end at Ocean Ave, back along Ocean Grove.
# Source: Geno, 2026-09-20, from Google Maps. Given as APPROXIMATE, and the
# archive says so too -- see LATITUDE_CONFLICT below. Do not treat these as
# surveyed values.
OUTLINE = [
    (40.21528, -74.01021),   # 1  "western head", Railroad Ave -- SHORT BY >=215 m.
                             #    Photographs at -74.01274 show open water extending
                             #    away from the camera; see geography.md. Left as
                             #    supplied rather than invented; the geofence buffer
                             #    covers the difference.
    (40.21558, -74.00845),   # 2  Main St bridge, north
    (40.21590, -74.00480),   # 3  Mattison Ave span, north
    (40.21601, -74.00195),   # 4  Embury Ave / Heck St footbridge, north
    (40.21608, -73.99975),   # 5  Pilgrim Pathway footbridge, north
    (40.21625, -73.99690),   # 6  Ocean Ave, north-east corner
    (40.21575, -73.99690),   # 7  Ocean Ave, south-east corner
    (40.21568, -73.99975),   # 8  Pilgrim Pathway footbridge, south
    (40.21560, -74.00195),   # 9  Embury Ave / Heck St footbridge, south
    (40.21542, -74.00480),   # 10 Lake Ave, south
    (40.21515, -74.00845),   # 11 Main St bridge, south
]

LATITUDE_CONFLICT = """\
The outline and the photographs disagree, and it is not a small disagreement.

Tested against 219 photos from FOUR cameras (iPhone 17, iPhone SE, Pixel 9, and
the Pixel's sibling), only 41 fall inside this polygon. 92 are north of its north
shore and 52 south of its south shore -- which is EXPECTED, since photographs are
taken from banks and bridges, not from the water. That part is fine.

What is not fine is the size of the northern excursion at the east end.
IMG_3452-3456 (2026-09-20) sit at latitude 40.21741, about 160 m north of where
this outline puts the north shore at that longitude. Those frames show the
east-end gull raft ON the water, close to; the photographer cannot have been
160 m away from a lake he is photographing at that scale. The same holds for
2026-08-11 at the Carousel end.

The likeliest reading is that the outline's latitudes run roughly 100-150 m too
far south in the eastern half. A mean-offset test rules out a camera fault: the
mean photo latitude is only +23 m from the outline's mid-latitude, and the three
identifiable cameras agree with each other.

Separately, 5 photos (2026-03-10, 2026-09-10) sit 195-226 m WEST of the western
head at -74.01021. Either the lake continues west of Railroad Ave, or those were
taken looking back east from beyond it.

UNTIL THIS IS RESOLVED the buffers below are deliberately generous. They are
sized to admit every photograph already confirmed as on-lake, which means they
are absorbing the outline's error as well as the bank margin. Shrink them once
the east-end latitude is settled -- ONE reading of the lake's latitude where it
meets Ocean Avenue would do it."""

# Segments, east -> west from the ocean end, bounded by the THREE real crossings
# (Geno, 2026-09-20). Longitude only: it is the coordinate the archive and the
# supplied data agree on everywhere, and a segment is a stretch of lake, not a
# point. The previous scheme was bounded by photo-inferred crossings and stopped
# at -74.0029, leaving 510 m of the eastern lake in no segment at all.
SEGMENTS = [
    ('S1', -73.99690, -73.99975, 'Ocean Ave end -> Pilgrim Pathway'),
    ('S2', -73.99975, -74.00195, 'Pilgrim Pathway -> Heck St / Embury Ave'),
    ('S3', -74.00195, -74.00480, 'Heck St / Embury Ave -> Mattison Ave'),
    ('S4', -74.00480, -74.01021, 'Mattison Ave -> Railroad Ave, the western head'),
    ('S5', -74.01021, -74.02000, 'west of the Railroad Ave head — extent unresolved'),
]


def segment_for(lon):
    """-> 'S1'..'S5', or '' if the longitude is off the scale. East of the Ocean
    Avenue end returns '' rather than guessing: that is the sea."""
    if lon is None or lon > SEGMENTS[0][1]:
        return ''
    for name, e, w, _ in SEGMENTS:
        if w <= lon <= e:
            return name
    return ''


def segment_note(name):
    for n, _, _, d in SEGMENTS:
        if n == name: return d
    return ''


# Generous on purpose; see LATITUDE_CONFLICT. A false negative here silently
# drops a real observation, which is far worse than reviewing a stray photo.
BUFFER_ON = 250.0
BUFFER_NEAR = 450.0

_LAT0 = 40.216
_MY = 111320.0
_MX = _MY * math.cos(math.radians(_LAT0))


def _xy(lat, lon):
    return (lon * _MX, lat * _MY)


_P = [_xy(a, b) for a, b in OUTLINE]


def _inside(pt, poly=None):
    poly = poly or _P
    x, y = pt; ins = False; j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj-xi)*(y-yi)/((yj-yi) or 1e-12) + xi):
            ins = not ins
        j = i
    return ins


def _seg(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx-ax, by-ay; L = dx*dx + dy*dy
    t = 0 if L == 0 else max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / L))
    return math.hypot(px - (ax + t*dx), py - (ay + t*dy))


def distance_m(lat, lon):
    """Metres from the water. 0 means on the water itself."""
    if lat is None or lon is None:
        return None
    pt = _xy(lat, lon)
    if _inside(pt):
        return 0.0
    return min(_seg(pt, _P[i], _P[(i+1) % len(_P)]) for i in range(len(_P)))


def zone(lat, lon, on=BUFFER_ON, near=BUFFER_NEAR):
    """ON / NEAR / OFF / NOGPS — PROTOCOL.md 3, now measured from the water."""
    d = distance_m(lat, lon)
    if d is None: return 'NOGPS'
    if d <= on: return 'ON'
    if d <= near: return 'NEAR'
    return 'OFF'


def on_land(lat, lon, slack=BUFFER_ON):
    """True if a fix is implausibly far from the lake — a stale-fix check that
    does not depend on implied speed, and so catches a bad fix even when the
    frames around it are far apart in time. Complements framing.stale_fixes."""
    d = distance_m(lat, lon)
    return d is not None and d > slack


if __name__ == '__main__':
    import csv, collections
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lats = [p[0] for p in OUTLINE]; lons = [p[1] for p in OUTLINE]
    print(f'outline: {len(OUTLINE)} points, '
          f'{(max(lats)-min(lats))*_MY:.0f} m N-S x {(max(lons)-min(lons))*_MX:.0f} m E-W')
    print(f'buffers: ON <= {BUFFER_ON:.0f} m, NEAR <= {BUFFER_NEAR:.0f} m\n')
    rows = [r for r in csv.DictReader(open(os.path.join(ROOT, 'analysis', 'exif-index.csv')))
            if r['lat']]
    z = collections.Counter(zone(float(r['lat']), float(r['lon'])) for r in rows)
    print('archive:', dict(z))
    ds = sorted((distance_m(float(r['lat']), float(r['lon'])), r['file']) for r in rows)
    print(f'median distance from water: {ds[len(ds)//2][0]:.0f} m; max {ds[-1][0]:.0f} m')
    print()
    print(LATITUDE_CONFLICT)
