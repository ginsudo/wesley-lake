#!/usr/bin/env python3
"""Checks for the WHOLE pipeline — schema, census, framing, surfaces, lake,
observe, water and the detection stage. No network, no model, no photos needed
except the two small fixtures noted.

    python3 pipeline/test_pipeline.py

Was called test_detect.py, which by the end covered eight modules it did not
name.
"""
import os, re, sys, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import schema

fails = []
def check(name, cond, detail=''):
    print(f"{'ok  ' if cond else 'FAIL'}  {name}{('  -- ' + detail) if detail and not cond else ''}")
    if not cond: fails.append(name)

# 1. "none" is a clean no-op --------------------------------------------------
import providers
cfg = providers.config()
saved = cfg['roles']['detector']
check('config parses', isinstance(cfg.get('roles'), dict))
import copy
c2 = copy.deepcopy(cfg); c2['roles']['detector'] = 'none'
p = os.path.join(HERE, 'config.json')
orig = open(p).read()
try:
    open(p, 'w').write(json.dumps(c2))
    check('roles.detector "none" yields no provider', providers.get('detector') is None)
finally:
    open(p, 'w').write(orig)

# 2. the validator actually rejects, and detect.py attaches rather than drops --
# PROTOCOL.md section 6: a Tier D bird may never carry an individual_id.
bad = schema.blank('photos/x.HEIC', tier='D', individual_id='SWAN-A01')
probs = schema.validate(bad)
check('validator catches Tier D + individual_id', len(probs) == 1, str(probs))

bad2 = schema.blank('photos/x.HEIC', tier='A', individual_id='', marks='')
check('validator catches Tier A with no id and no mark', len(schema.validate(bad2)) == 2,
      str(schema.validate(bad2)))

bad3 = schema.blank('photos/x.HEIC'); bad3['features'].pop('legs')
check('validator catches a missing feature key',
      any('legs' in x for x in schema.validate(bad3)), str(schema.validate(bad3)))

# The stage must WRITE a failing record with its problems, never drop it.
# Exercised here by driving detect.py's record path with a stub detector whose
# boxes carry a deliberately invalid hint.
class StubDet:
    name = 'stub'; model = 'stub'; conf = 0.5; iou = 0.5; tile = 0; overlap = 0
    whole_frame = True
    def __init__(self, boxes): self.boxes = boxes
    def detect(self, path): return self.boxes

try:
    import detect
    import glob
    src = sorted(glob.glob(os.path.join(ROOT, 'photos', '2026-03-30', '*')))[:1]
    if not src:
        check('fixture photo present', False, 'photos/2026-03-30 empty — skipped')
    else:
        with tempfile.TemporaryDirectory() as td:
            pd = os.path.join(td, 'photos'); os.makedirs(pd)
            os.symlink(src[0], os.path.join(pd, os.path.basename(src[0])))
            oj = os.path.join(td, 'out.json')
            _real_blank = schema.blank
            def poisoned(photo, **kw):
                r = _real_blank(photo, **kw)
                r['tier'] = 'D'; r['individual_id'] = 'GBHE-A01'   # forbidden combo
                return r
            schema.blank = poisoned
            try:
                out = detect.detect_date('x', StubDet([(0.30, 0.30, 0.42, 0.55, 0.91)]),
                                         photo_dir=pd, work_dir=os.path.join(td, 'w'),
                                         out_json=oj, overlays=False, verbose=False)
            finally:
                schema.blank = _real_blank
            rec = out['records'][0]
            check('invalid record is written, not dropped', len(out['records']) == 1)
            check('invalid record carries problems', 'problems' in rec and rec['problems'],
                  str(rec.get('problems')))
            check('invalid record counted in validation_problems',
                  out['validation_problems'] == 1 and out['validated_clean'] == 0,
                  f"clean={out['validated_clean']} bad={out['validation_problems']}")
            check('crop written at native resolution', rec['crop'] and
                  os.path.exists(os.path.join(td, 'w', 'crops',
                                              os.path.basename(rec['crop']))))
except Exception as e:
    check('stage record path', False, repr(e))

# 3. census rule and surfaces, PROTOCOL.md 5b ---------------------------------
import surfaces, census

reg = surfaces.registry()
check('geography.md mat registry parses', len(reg) >= 3, f'{len(reg)} rows')
check('unresolved mats are not assignable',
      all(not m['confirmed'] or m['id'] in surfaces.mat_ids() for m in reg)
      and not any(m['id'] in surfaces.mat_ids() for m in reg if not m['confirmed']),
      str(surfaces.mat_ids()))
check('MAT-unassigned is always assignable', surfaces.UNASSIGNED_MAT in surfaces.mat_ids())

# The mats FLOAT and drift (Geno, 2026-09-20) and the planting is deciduous, so
# the registry must distinguish a durable structural mark from a seasonal or
# positional cue. PROTOCOL.md 5b.
check('registry exposes durable-mark status',
      all('has_durable_mark' in m for m in reg))
check('at least one mat has a durable mark', any(m['has_durable_mark'] for m in reg),
      'no mat is matchable across seasons — check geography.md')
check('mats without a durable mark are flagged, not silently promoted',
      any(not m['has_durable_mark'] for m in reg),
      'every mat claims a durable mark — suspicious, verify geography.md')
for phrase in ('None identified', 'Not yet photographed at the waterline',
               '—', 'N/A', 'unknown', 'TBD', ''):
    check(f'"{phrase or "(empty)"}" is not read as a durable mark',
          not surfaces._has_mark(phrase))
for phrase in ('**A substantial dark log** lying across the base',
               'Round planting ports, 6 of them, in an L'):
    check(f'"{phrase[:34]}..." IS read as a durable mark', surfaces._has_mark(phrase))
check('exactly the mats with a recorded mark are flagged',
      [m['id'] for m in reg if m['has_durable_mark']] == ['MAT-01'],
      str([m['id'] for m in reg if m['has_durable_mark']]))
check('no mat carries coordinates — a drifting mat has no position identity',
      not any(re.search(r'-?7[34]\.\d{3}|40\.2\d{3}', m['durable_mark'] + m['id'])
              for m in reg),
      str([m['id'] for m in reg if re.search(r'\d{2}\.\d{3}', m['durable_mark'])]))
def _code_identifiers(fname):
    """Identifiers and string literals in real code — docstrings excluded, so a
    comment explaining why we do NOT use GPS does not trip the check below."""
    import ast
    tree = ast.parse(open(os.path.join(HERE, fname)).read())
    # ast.walk is flat, so skipping the Expr wrapper would not skip its child.
    # Collect the docstring Constant nodes and exclude them by identity.
    docs = {id(n.value) for n in ast.walk(tree)
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    for node in ast.walk(tree):
        if id(node) in docs:
            continue
        if isinstance(node, ast.Name): yield node.id
        elif isinstance(node, ast.Attribute): yield node.attr
        elif isinstance(node, ast.arg): yield node.arg
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.value

_geo = [t for t in _code_identifiers('surfaces.py')
        if re.search(r'\b(lat|lon|latitude|longitude|gps|coord)\b', str(t), re.I)]
check('surfaces.py resolves no mat from GPS — a drifting mat has no position identity',
      not _geo, str(_geo[:5]))

check('open_water is core', schema.census_of('open_water') == 'core')
check('shallows is core (wader standing in the lake)', schema.census_of('shallows') == 'core')
check('island_or_mat is core', schema.census_of('island_or_mat') == 'core')
check('shoreline_edge is noted (on the bank)', schema.census_of('shoreline_edge') == 'noted')
check('in_flight is noted', schema.census_of('in_flight') == 'noted')
check('man_made_perch is noted (incl. pedal boats)',
      schema.census_of('man_made_perch') == 'noted')
check('every stratum has a census class',
      all(st in schema.STRATUM_CENSUS for st in schema.STRATA),
      str([st for st in schema.STRATA if st not in schema.STRATUM_CENSUS]))

def one(**kw):
    r = schema.blank('photos/x.HEIC', **kw); return schema.validate(r)

check('census_class contradicting stratum is caught',
      any('contradicts' in x for x in
          one(stratum='in_flight', census_class='core', surface='open_water')))
check('stratum set but census_class left undetermined is caught',
      any('undetermined' in x for x in one(stratum='open_water')))
check('core bird with no surface is caught',
      any('no surface' in x for x in one(stratum='open_water', census_class='core')))
check('island_or_mat with no surface is caught',
      any('name the mat' in x for x in one(stratum='island_or_mat', census_class='core')))
check('unknown mat ID is caught',
      any('not in the geography.md mat registry' in x for x in
          one(stratum='island_or_mat', census_class='core', surface='MAT-99')))
check('unresolved mat ID is rejected as a surface',
      any('not in the geography.md mat registry' in x for x in
          one(stratum='island_or_mat', census_class='core', surface='MAT-?a')))
check('a real mat ID validates clean',
      one(stratum='island_or_mat', census_class='core', surface='MAT-01') == [])
check('MAT-unassigned validates clean',
      one(stratum='island_or_mat', census_class='core',
          surface=schema.UNASSIGNED_MAT) == [])
check('mat ID on a non-mat stratum is caught',
      any('not island_or_mat' in x for x in
          one(stratum='in_flight', census_class='noted', surface='MAT-01')))
check('detector record (no stratum) stays clean and uncounted',
      one() == [] and schema.blank('x')['census_class'] == 'undetermined')

t = census.tally([
    schema.blank('x', stratum='open_water', census_class='core',
                 surface='open_water', count=4),
    schema.blank('x', stratum='island_or_mat', census_class='core',
                 surface='MAT-01', count=5, count_range=[5, 6]),
    schema.blank('x', stratum='in_flight', census_class='noted', count=3),
    schema.blank('x', count=9),                       # undetermined
])
check('census: core sums only on-lake birds', t['core'] == 9, str(t['core']))
check('census: ranges survive to the total', t['core_hi'] == 10, str(t['core_hi']))
check('census: noted kept separate', t['noted'] == 3, str(t['noted']))
check('census: undetermined counts toward nothing',
      t['undetermined'] == 9 and t['core'] == 9 and t['noted'] == 3)
check('census: per-surface tally', dict(t['by_surface']) == {'open_water': 4, 'MAT-01': 5},
      str(dict(t['by_surface'])))

# 4. framing: not double-counting re-photographed birds, PROTOCOL.md 9 -------
import framing

check('framing self-check reproduces Entry 4 grouping',
      framing.self_check(verbose=False) == [],
      str(framing.self_check(verbose=False)))

rows = framing.load('2026-09-20')['2026-09-20']
st = framing.stale_fixes(rows)
check('stale fix IMG_3488 detected', 'IMG_3488.HEIC' in st)
check('its innocent neighbour IMG_3487 is NOT flagged', 'IMG_3487.HEIC' not in st,
      'the DECISIVE ratio should spare a frame merely adjacent to a bad fix')

# Regressions. Both of these produced phantom "stale fixes" before MIN_JUMP_M.
def _synth(steps):
    """steps = [(dt_seconds, metres_east)] -> rows framing.stale_fixes can read."""
    rows, t, lon = [], 0, -74.006
    for i, (dt, m) in enumerate([(0, 0)] + steps):
        t += dt; lon += m / 84600.0
        rows.append({'file': f'IMG_{9000+i}.HEIC', 'lat': 40.216, 'lon': lon,
                     'dt': f'2026:01:01 {t//3600:02d}:{t%3600//60:02d}:{t%60:02d}'})
    return rows

check('same-second frames are not a stale fix (was infinite speed)',
      framing.stale_fixes(_synth([(0, 0.0), (5, 2.0)])) == {},
      'zero time gap must be skipped, not divided by')
check('small GPS jitter over a short gap is not a stale fix',
      framing.stale_fixes(_synth([(1, 3.8), (5, 2.0)])) == {},
      '3.8 m in 1 s reads as 3.8 m/s but is ordinary jitter')
check('a real 60 m jump and back IS a stale fix',
      len(framing.stale_fixes(_synth([(4, 60.0), (4, -60.0), (30, 5.0)]))) == 1,
      str(framing.stale_fixes(_synth([(4, 60.0), (4, -60.0), (30, 5.0)]))))
check('archive-wide stale fixes are few and all large jumps',
      all(any(f'{v:.1f} m/s' in why for v in (8.0, 12.1, 15.6, 16.8, 19.9))
          for d_, rs in framing.load().items()
          for why in framing.stale_fixes(rs).values()),
      'a surviving flag should be an unmistakable jump, not a marginal one')

# zoom classification. This phone has a 5.96 mm main and a 2.22 mm ultrawide and
# NO telephoto, so any rise in 35mm-equivalent within one lens is a sensor crop.
W = {'focal': 5.96, 'eq35': 26}
check('2x (52mm-eq) is a real sensor crop',
      framing.zoom_class(W, {'focal': 5.96, 'eq35': 52})[0] == 'real_crop')
check('5x (143mm-eq) on the same lens is interpolated',
      framing.zoom_class(W, {'focal': 5.96, 'eq35': 143})[0] == 'interpolated')
check('10x (272mm-eq) is interpolated',
      framing.zoom_class(W, {'focal': 5.96, 'eq35': 272})[0] == 'interpolated')
check('ultrawide -> wide is a real lens change, not a crop',
      framing.zoom_class({'focal': 2.22, 'eq35': 14},
                         {'focal': 5.96, 'eq35': 45})[0] == 'lens_change')

bursts = framing.zoom_bursts(rows)
flat = {f for b in bursts for f in b}
check('the heron zoom burst is found',
      any(set(b) >= {'IMG_3478.HEIC', 'IMG_3479.HEIC'} for b in bursts), str(bursts[:3]))
check('zoom bursts never span more than the gap allows',
      all(0 <= framing.track.secs(
              next(r for r in rows if r['file'] == b[i+1])['dt'])
            - framing.track.secs(next(r for r in rows if r['file'] == b[i])['dt'])
          <= framing.ZOOM_GAP_S for b in bursts for i in range(len(b)-1)))
check('framing decides nothing from pixels — no image is opened',
      'Image' not in open(os.path.join(HERE, 'framing.py')).read(),
      'PROTOCOL.md 6: identity must not come from image similarity')

check('assign() gives every frame an event, including stale-fixed ones',
      all(framing.assign(rows)[1].get(r['file']) is not None for r in rows),
      'a record with no event slips past the census double-counting guard')
check('the stale frame inherits a real event',
      framing.assign(rows)[1].get('IMG_3488.HEIC') is not None)

# 5. the count_basis contract ------------------------------------------------
base = dict(stratum='open_water', surface='open_water', census_class='core')
check('identified bird with a count needs a count_basis',
      any('count_basis' in x for x in one(species='Mallard', count=3, **base)))
check("'max_simultaneous' without frames is caught",
      any('needs `frames`' in x for x in
          one(species='Mallard', count=3, count_basis='max_simultaneous', **base)))
check("'single_frame' spanning several frames is caught",
      any('single_frame' in x for x in
          one(species='Mallard', count=3, count_basis='single_frame',
              frames=['a', 'b'], **base)))
check('a well-formed counted record validates clean',
      one(species='Mallard', count=3, count_basis='max_simultaneous',
          frames=['a', 'b'], **base) == [])
check('detector records stay clean under the new rules',
      schema.validate(schema.blank('x')) == [])

def mk(**k):
    kw = {**base, 'count_basis': 'max_simultaneous', 'frames': ['a'], **k}
    return schema.blank('p', **kw)
t2 = census.tally([mk(species='Mallard', count=5, event=2),
                   mk(species='Mallard', count=3, event=2),      # zoomed re-view
                   mk(species='Mallard', count=4, event=7),      # different event
                   mk(species='Mute Swan', count=1, event=2)])
t2b = census.tally([mk(species='Mallard', count=5, event=1, stratum='shoreline_edge',
                       surface='', census_class='noted'),
                    mk(species='Mallard', count=4, event=1)])
check('same species, same event, DIFFERENT stratum is not a duplicate',
      t2b['core'] == 4 and t2b['noted'] == 5,
      f"core={t2b['core']} noted={t2b['noted']} — a split bank/water record must survive")

t2c = census.tally([mk(species='Mute Swan', count=1, event=1, age_class='adult'),
                    mk(species='Mute Swan', count=2, event=1, age_class='cygnet')])
check('an adult and its cygnets are additive, not duplicates',
      t2c['core'] == 3, f"core={t2c['core']} — age_class must be in the dedup key")

t0 = census.tally([mk(species='', count=0, stratum='island_or_mat',
                      surface=schema.UNASSIGNED_MAT, event=1)])
check('count=0 is a real count, not a missing one',
      t0['core'] == 0, f"core={t0['core']} — an empty mat must not count as a bird")
tm = census.tally([mk(species='X', count=5, count_range='bad', event=1)])
check('a count=0 record creates no species row',
      not t0['core_species'], str(dict(t0['core_species'])))
check('a malformed count_range does not crash the tally', tm['core'] == 5)
check('a malformed count_range is reported', any('count_range' in x for x in tm['problems']))
check('count outside its own range is caught',
      any('outside its own count_range' in x for x in
          one(species='X', count=9, count_range=[2,3], count_basis='max_simultaneous',
              frames=['a'], **base)))
check('count_exact plus a range is caught',
      any('pick one' in x for x in
          one(species='X', count=3, count_exact=True, count_range=[3,4],
              count_basis='max_simultaneous', frames=['a'], **base)))
te = census.tally([mk(species='X', count=3, event=None)])
check('a record with no event is flagged as uncheckable',
      any('no event' in x for x in te['problems']))

check('census does not sum one species twice in one event',
      t2['core'] == 10, f"got {t2['core']}, naive sum is 13")
check('census says which record it dropped', len(t2['not_summed']) == 1, str(t2['not_summed']))
t3 = census.tally([mk(species='Mallard', count=5, event=2),
                   mk(species='Mallard', count=3, event=2, count_basis='additive')])
check('an explicit `additive` record IS summed', t3['core'] == 8, str(t3['core']))

# 6. observe.py: derived metadata, not typed metadata -------------------------
import observe
check('observe.derive fills event/stop/census_class from the pipeline',
      all(k in observe.derive('2026-09-20',
              schema.blank('photos/2026-09-20/IMG_3461.HEIC', stratum='island_or_mat',
                           surface='MAT-01', frames=['IMG_3461.HEIC']))[0]
          for k in ('event', 'stop', 'census_class', 'detections_in_frames')))
_d, _p = observe.derive('2026-09-20',
    schema.blank('photos/2026-09-20/IMG_3461.HEIC', stratum='island_or_mat',
                 surface='MAT-01', frames=['IMG_3461.HEIC']))
check('derived event is the real one, not a typed guess', _d['event'] == 2, str(_d['event']))
check('provenance links the record back to detections', len(_d['detections_in_frames']) > 0)
check('census_class is derived from stratum', _d['census_class'] == 'core')
_g, _gp = observe.derive('2026-09-20',
    schema.blank('photos/2026-09-20/IMG_3461.HEIC', frames=['IMG_9999.HEIC']))
check('a cited frame that is not on disk is caught',
      any('not on disk' in x for x in _gp), str(_gp))
check('re-deriving the whole archive is idempotent and clean',
      observe.recheck(write=False) == 0)

# 7. the lake outline as geofence, PROTOCOL.md 3 -----------------------------
import lake
check('a point on the water is 0 m from the outline',
      lake.distance_m(40.21570, -74.00480) == 0.0)
check('a bank photo is a short distance out, not inside',
      0 < lake.distance_m(40.21660, -74.00480) < 150)
check('every archived on-lake photo passes the geofence',
      all(lake.zone(float(r['lat']), float(r['lon'])) == 'ON'
          for r in __import__('csv').DictReader(
              open(os.path.join(ROOT, 'analysis', 'derived', 'exif-index.csv'))) if r['lat']),
      'a geofence that rejects a real observation is worse than a loose one')
check('somewhere obviously not the lake is OFF',
      lake.zone(40.2300, -74.0100) == 'OFF')           # ~1.5 km north, inland
check('the outline closes (first point is not repeated)',
      lake.OUTLINE[0] != lake.OUTLINE[-1], 'the polygon helper closes it implicitly')
check('the outline/archive conflict is documented, not buried',
      'LATITUDE_CONFLICT' in open(os.path.join(HERE, 'lake.py')).read()
      and len(lake.LATITUDE_CONFLICT) > 400)
check('buffers are generous while the conflict stands',
      lake.BUFFER_ON >= 200,
      'shrink only once the east-end latitude is settled')

check('segments are bounded by the three real crossings',
      [x[0] for x in lake.SEGMENTS] == ['S1','S2','S3','S4','S5'])
check('segment bounds are contiguous, no gaps',
      all(abs(lake.SEGMENTS[i][2] - lake.SEGMENTS[i+1][1]) < 1e-9
          for i in range(len(lake.SEGMENTS)-1)),
      'the old scheme left 510 m of the eastern lake in no segment')
check('a longitude at the Mattison span lands in S3 or S4',
      lake.segment_for(-74.00480) in ('S3','S4'))
check('east of the Ocean Ave end returns no segment, not a guess',
      lake.segment_for(-73.9900) == '')
check('every record now carries a derived segment',
      all(r.get('segment') for f in __import__('glob').glob(
              os.path.join(ROOT,'analysis','records','*-observations.json'))
          for r in json.load(open(f))['records']),
      'observe.py derives segment; none should be blank')
_recs = [r for f in __import__('glob').glob(
             os.path.join(ROOT,'analysis','records','*-observations.json'))
         for r in json.load(open(f))['records']]
check('S1 has never been photographed',
      not any(r.get('segment') == 'S1' for r in _recs),
      'if this fails someone has reached the Ocean Ave end — update geography.md')
check('S2 has been photographed, and every visit was birdless',
      any(r.get('segment') == 'S2' for r in _recs)
      and all((r.get('count') or 0) == 0 for r in _recs if r.get('segment') == 'S2'),
      'the only S2 records are the two 2025 dates, both no-bird observations')

# 8. water quality, PROTOCOL.md 3a -------------------------------------------
import water
_st = water.stations()
check('geography.md defines at least one water station', 'WQ-1' in _st, str(sorted(_st)))
check('both record types carry a schema_version',
      schema.blank('x').get('schema_version') == schema.SCHEMA_VERSION
      and water.blank('2026-01-01','WQ-1').get('schema_version') == water.SCHEMA_VERSION,
      'their absence meant two rounds of hand-backfilling when the schema moved')
check('a record from an older schema is caught, not silently accepted',
      any('schema_version' in x for x in
          schema.validate({**schema.blank('x'), 'schema_version': 1})))
check('every migration step is documented',
      set(schema.MIGRATIONS) == set(range(1, schema.SCHEMA_VERSION + 1)),
      str(sorted(schema.MIGRATIONS)))
check('derived and authored records live in separate directories',
      os.path.isdir(os.path.join(ROOT,'analysis','derived'))
      and os.path.isdir(os.path.join(ROOT,'analysis','records'))
      and not glob.glob(os.path.join(ROOT,'analysis','*.json')),
      'irreplaceable records must not sit beside regenerable output')
check('analysis/ says which half is safe to delete',
      'NEVER DELETE' in open(os.path.join(ROOT,'analysis','README.md')).read())
check('a blank water record is not clean — it must cite frames',
      any('no frames' in x for x in water.validate(water.blank('2026-01-01','WQ-1'))))

def _w(**k):
    base = dict(frames=['a.HEIC'], surface_state='glassy', ice_cover='none',
                organic_load='clear', water_level='at_sill', tide='unknown',
                marginal_vegetation='sparse')
    return water.validate(water.blank('2026-01-01', 'WQ-1', **{**base, **k}), _st)

check('a well-formed water record validates clean', _w() == [], str(_w()))
check('an unknown station is caught',
      any('unknown station' in x for x in
          water.validate(water.blank('2026-01-01','WQ-9', frames=['a']), _st)))
check('a bad category is caught',
      any('bad organic_load' in x for x in _w(organic_load='quite_a_lot')))
check('an exact litter count through wind-whipped water is refused',
      any('cannot be counted exactly' in x for x in
          _w(surface_state='wind_whipped', litter_count=5, litter_exact=True,
             litter_types=['plastic_film'])),
      'surface_state is a quality flag on the observation, not data about the lake')
check('a range through wind-whipped water is fine',
      _w(surface_state='wind_whipped', litter_count=5, litter_range=[3,9],
         litter_types=['plastic_film']) == [])
check('litter_count without types is caught',
      any('must be given together' in x for x in _w(litter_count=4)))
check('an unknown litter type is caught',
      any('unknown litter_types' in x for x in
          _w(litter_count=1, litter_types=['shopping_trolley'])))
check('complete ice with a non-frozen surface is caught',
      any('ice_cover' in x for x in _w(ice_cover='complete', surface_state='glassy')))
check('count outside its own range is caught',
      any('outside its own litter_range' in x for x in
          _w(litter_count=99, litter_range=[1,5], litter_types=['other'])))
# water.py may now OPEN images — prepare() builds the review sheet. What must
# never happen is a judgement computed from pixels. So: image use is allowed in
# prepare() and nowhere else, and prepare() must assign no judged field.
import ast as _ast
_wtree = _ast.parse(open(os.path.join(HERE, 'water.py')).read())
_img_in = set()
for _fn in [n for n in _ast.walk(_wtree) if isinstance(n, _ast.FunctionDef)]:
    for _n in _ast.walk(_fn):
        if isinstance(_n, _ast.Attribute) and _n.attr in ('open', 'Stat') \
           and isinstance(getattr(_n, 'value', None), _ast.Name) \
           and _n.value.id in ('Image', 'ImageStat'):
            _img_in.add(_fn.name)
check('only prepare() touches images in water.py', _img_in <= {'prepare'},
      f'{sorted(_img_in)} — a judgement must never be computed from pixels, '
      'because illumination dominates them')
_prep = [n for n in _ast.walk(_wtree)
         if isinstance(n, _ast.FunctionDef) and n.name == 'prepare']
_judged = {'water_appearance', 'surface_state', 'ice_cover', 'organic_load',
           'water_level', 'marginal_vegetation', 'litter_count', 'sky'}
_assigned = {t.id for f in _prep for n in _ast.walk(f)
             if isinstance(n, _ast.Assign) for t in n.targets
             if isinstance(t, _ast.Name)}
check('prepare() assigns no judged field', not (_assigned & _judged),
      str(sorted(_assigned & _judged)) + ' — prepare builds the material, '
      'a person judges it')

_wf = os.path.join(ROOT,'analysis','records','2026-09-21-water.json')
if os.path.exists(_wf):
    _wd = json.load(open(_wf))
    check('the first real water observation validates clean',
          _wd['validation_problems'] == 0)
    check('it records "nothing unusual" rather than staying silent',
          'NOTHING UNUSUAL' in _wd['records'][0]['notes'])

# 9. the pipeline is honest about what it cannot do ---------------------------
import status
_all = status.dates()
check('status sees every date on disk', len(_all) == len(glob.glob(
          os.path.join(ROOT, 'photos', '2*'))))
_s = status.state('2026-09-21')
check('status reports the machine half', _s['swept'] and _s['photos'] == 43,
      str(_s))
check('status reports the eyes half separately',
      'birds' in _s and 'water' in _s)
check('run.py runs the water stage as well as the detector',
      'water_stage()' in open(os.path.join(HERE, 'run.py')).read()
      and 'detect_stage()' in open(os.path.join(HERE, 'run.py')).read(),
      'the standard pipeline must cover birdlife AND water condition')
check('run.py ends by saying what still needs eyes',
      'status.report' in open(os.path.join(HERE, 'run.py')).read(),
      'it used to end pointing at contact sheets that are no longer the review artefact')
check('water.prepare builds a sheet without judging anything',
      'Image.open' in open(os.path.join(HERE, 'water.py')).read()
      and 'water_appearance=' not in open(os.path.join(HERE, 'water.py')).read()
          .split('def prepare')[1].split('def ')[0],
      'prepare() may open images; it must not set any judged field')
check('every analysis record file uses one naming convention',
      not glob.glob(os.path.join(ROOT, 'analysis', 'records', '*-core-count.json')),
      'a stray -core-count.json meant globs of *-observations.json silently '
      'skipped the best-analysed date')
check('the segment tests now include 2026-09-20',
      any('2026-09-20' in f for f in glob.glob(
          os.path.join(ROOT, 'analysis', 'records', '*-observations.json'))))

# 10. provenance guards — an external photograph is not an observation -------
check('every record defaults to own_walk', schema.blank('x')['source'] == 'own_walk'
      and water.blank('2026-01-01','WQ-1')['source'] == 'own_walk')
check('external without a source_note is caught',
      any('source_note' in x for x in schema.validate(
          schema.blank('x', source='external'))))
check('external with count_exact is refused',
      any('count exactly' in x for x in schema.validate(
          schema.blank('x', source='external', source_note='web', count=3,
                       count_exact=True))),
      'framing and moment were chosen by someone else')
check('external with additive counting is refused',
      any('additivity is a claim' in x for x in schema.validate(
          schema.blank('x', source='external', source_note='web', count=3,
                       count_basis='additive'))))
check('external water cannot carry a level or a litter count',
      len([x for x in water.validate(water.blank('2026-01-01','WQ-1', frames=['a'],
           source='external', source_note='web', water_level='at_sill',
           tide='unknown', litter_count=2, litter_types=['other']))
           if 'external' in x]) == 2)
_ext = census.tally([
    schema.blank('a', species='Mallard', count=4, stratum='open_water',
                 surface='open_water', census_class='core',
                 count_basis='max_simultaneous', frames=['a'], event=1),
    schema.blank('b', species='Brant', count=30, stratum='open_water',
                 surface='open_water', census_class='core',
                 count_basis='max_simultaneous', frames=['b'], event=1,
                 source='external', source_note='web')])
check('an external record never reaches the core count',
      _ext['core'] == 4 and _ext['presence_only'].get('Brant') == 1,
      f"core={_ext['core']} — every counting rule assumes one observer on one walk")
check('a GPS-less photo is not filed into the dated record',
      "'_no-gps'" in open(os.path.join(HERE, 'run.py')).read(),
      'PROTOCOL.md 3: never infer a location silently')
check('all records migrated to the current schema versions',
      all(r.get('schema_version') == schema.SCHEMA_VERSION
          for f in glob.glob(os.path.join(ROOT,'analysis','records','*-observations.json'))
          for r in json.load(open(f))['records']))

# 11. fractional-box contract of base.Detector --------------------------------
from providers.base import Detector
check('base.Detector.detect is abstract', 
      Detector.detect.__doc__ and 'fractional' in Detector.detect.__doc__)

print()
print(f'{len(fails)} failure(s)' if fails else 'all checks passed')
sys.exit(1 if fails else 0)
