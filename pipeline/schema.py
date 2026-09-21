"""The observation record. This contract is fixed; providers are swappable.

VERSIONING. Every record carries `schema_version`. This field exists because
its absence hurt: when this schema gained `census_class` and later
`count_basis`, every file already on disk silently became invalid, and the fix
was two rounds of hand-backfilling with no way to tell old records from new.
Bump SCHEMA_VERSION whenever a field is added, removed or given new meaning,
and note the change in MIGRATIONS below so a reader of an old file knows what
it was written against.
Mirrors PROTOCOL.md section 5 — change them together."""
SCHEMA_VERSION = 3
MIGRATIONS = {
    1: 'original — species, count, stratum, activity, tier, features',
    2: 'added census_class + surface (PROTOCOL.md 5b); stratum gained `shallows`',
    3: 'added count_basis + frames (PROTOCOL.md 9); stop/event/segment derived '
       'by observe.py rather than typed',
}

STRATA = ['open_water','shallows','island_or_mat',
          'shoreline_edge','bank_vegetation','overhanging_branch',
          'in_flight','man_made_perch']

# PROTOCOL.md section 5b. The core count is birds ON THE LAKE SURFACE: floating on
# the water, standing in it, or on a floating mat. Everything else -- flying over,
# standing on the bank, in a tree, on a dock or railing -- is recorded, and
# recorded fully, but kept OUT of the core count so the headline number means one
# thing. Census class is derived from stratum; it is never a free judgement.
CENSUS = ['core','noted','undetermined']
STRATUM_CENSUS = {
    'open_water':        'core',    # floating on the water
    'shallows':          'core',    # standing in the water, bottom-supported (waders)
    'island_or_mat':     'core',    # on a floating island -- see SURFACE below
    'shoreline_edge':    'noted',   # on the bank at the waterline, on ground
    'bank_vegetation':   'noted',
    'overhanging_branch':'noted',   # over the lake, but in a tree
    'in_flight':         'noted',
    'man_made_perch':    'noted',   # dock, railing, pedal boat, pipe -- all noted
}

# Which surface the bird was on. For core birds this is never blank: open water is
# a surface, and every floating mat is its own surface with an ID from the registry
# in geography.md. That is the whole point of tracking mats individually -- "5
# cormorants on a mat" is a weaker record than "5 cormorants on MAT-01".
OPEN_WATER_SURFACE = 'open_water'
UNASSIGNED_MAT = 'MAT-unassigned'   # honest placeholder: a mat, but which one is unread

# How a count was arrived at. PROTOCOL.md section 9: "Distinguish 'same photo
# re-counted' from 'additive new birds.'" That distinction used to live in prose
# in the notes field, where nothing could check it. Now it is structured, and
# census.py refuses to sum two records of one species in one sighting event
# unless one of them says `additive` out loud.
COUNT_BASIS = [
    'single_frame',      # counted in one frame; says nothing about other frames
    'max_simultaneous',  # largest number seen at once across `frames` — the default
    'additive',          # genuinely NEW birds, not already counted in this event
    'unknown',
]
ACTIVITIES = ['loafing','sleeping','preening','wing_drying','dabbling','diving',
              'plunge_diving','stalking','gleaning','walking','aggression',
              'courtship','brooding','flying_through','taking_off','landing']
CONFIDENCE = ['certain','probable','possible','unknown']
TIERS = ['A','B','C','D']
FEATURE_KEYS = ['bill','legs','head','breast_flank','wing_tail','asymmetries','size']

def blank(photo, **kw):
    r = dict(schema_version=SCHEMA_VERSION,
             photo=photo, species='', confidence='unknown', count=None, count_exact=False,
             age_class='', stratum='', activity='', associations='',
             census_class='undetermined', surface='',
             stop=None, event=None, frames=None, count_basis='unknown',
             features={k: 'not visible' for k in FEATURE_KEYS},
             marks_checked=False, marks='', tier='D', individual_id='',
             notes='', provider='', model='')
    r.update(kw); return r


def census_of(stratum):
    """Census class implied by a stratum. 'undetermined' if the stratum is unset."""
    return STRATUM_CENSUS.get(stratum, 'undetermined') if stratum else 'undetermined'


def known_surfaces():
    """Mat IDs from geography.md, via surfaces.py. Returns None if the registry
    cannot be read -- callers then skip the membership check rather than
    inventing a failure."""
    try:
        import surfaces
        return set(surfaces.mat_ids())
    except Exception:
        return None

def validate(r):
    """Return list of problems. Empty list = clean. Never silently coerce."""
    p = []
    if r.get('confidence') not in CONFIDENCE: p.append(f"bad confidence {r.get('confidence')!r}")
    if r.get('stratum') and r['stratum'] not in STRATA: p.append(f"bad stratum {r['stratum']!r}")
    if r.get('activity') and r['activity'] not in ACTIVITIES: p.append(f"bad activity {r['activity']!r}")
    if r.get('tier') not in TIERS: p.append(f"bad tier {r.get('tier')!r}")
    if r.get('tier') == 'D' and r.get('individual_id'):
        p.append("Tier D bird carries an individual_id — forbidden by PROTOCOL.md section 6")
    if r.get('tier') in ('A','B') and not r.get('individual_id'):
        p.append(f"Tier {r['tier']} needs an individual_id")
    if r.get('tier') == 'A' and not r.get('marks'):
        p.append("Tier A requires a recorded hard mark")
    miss = [k for k in FEATURE_KEYS if k not in (r.get('features') or {})]
    if miss: p.append(f"missing feature keys: {miss}")

    v = r.get('schema_version')
    if v is None:
        p.append(f"no schema_version — written before versioning; current is "
                 f"{SCHEMA_VERSION}, see schema.MIGRATIONS")
    elif v != SCHEMA_VERSION:
        p.append(f"schema_version {v} but current is {SCHEMA_VERSION} "
                 f"({MIGRATIONS.get(SCHEMA_VERSION, '?')}) — migrate or re-derive")

    cb = r.get('count_basis')
    if cb not in COUNT_BASIS:
        p.append(f"bad count_basis {cb!r}")
    cr = r.get('count_range')
    if cr is not None:
        if not (isinstance(cr, (list, tuple)) and len(cr) == 2
                and all(isinstance(x, int) for x in cr)):
            p.append(f"count_range must be [low, high] integers, got {cr!r}")
        elif cr[0] > cr[1]:
            p.append(f"count_range {cr!r} is inverted")
        elif r.get('count') is not None and not (cr[0] <= r['count'] <= cr[1]):
            p.append(f"count {r['count']} is outside its own count_range {cr!r}")
        elif r.get('count_exact'):
            p.append("count_exact is True but a count_range is given — pick one")

    fr = r.get('frames')
    if fr is not None and not isinstance(fr, list):
        p.append("frames must be a list of filenames")
    if cb == 'max_simultaneous' and not fr:
        p.append("count_basis 'max_simultaneous' needs `frames` — which frames it spans")
    if cb == 'single_frame' and fr and len(fr) > 1:
        p.append(f"count_basis 'single_frame' but {len(fr)} frames listed — "
                 "use max_simultaneous or additive")
    if r.get('count') and cb == 'unknown' and r.get('species'):
        p.append("an identified bird with a count needs a count_basis "
                 "(PROTOCOL.md section 9) — say how it was counted")

    # --- census rule, PROTOCOL.md 5b -------------------------------------
    cc, st, sf = r.get('census_class'), r.get('stratum'), r.get('surface') or ''
    if cc not in CENSUS:
        p.append(f"bad census_class {cc!r}")
    elif st and st in STRATUM_CENSUS and cc != 'undetermined' and cc != STRATUM_CENSUS[st]:
        p.append(f"census_class {cc!r} contradicts stratum {st!r} "
                 f"(PROTOCOL.md 5b says {STRATUM_CENSUS[st]!r}) — fix one, do not coerce")
    if st and cc == 'undetermined':
        p.append(f"stratum {st!r} is set but census_class is still 'undetermined'")

    # A core bird is on some surface, and we say which. A mat bird names its mat.
    if cc == 'core' and not sf:
        p.append("core-count bird with no surface — say open_water or a mat ID")
    if st == 'island_or_mat':
        if not sf:
            p.append("island_or_mat with no surface — name the mat "
                     "(geography.md registry) or use MAT-unassigned")
        elif sf.startswith('MAT-') and sf != UNASSIGNED_MAT:
            known = known_surfaces()
            if known is not None and sf not in known:
                p.append(f"surface {sf!r} is not in the geography.md mat registry")
    elif sf.startswith('MAT-') and st:
        p.append(f"surface {sf!r} names a mat but stratum is {st!r}, not island_or_mat")
    return p

PROMPT = """You are identifying birds in a single photograph for a rigorous field log.

Read the image at: {path}

Context: Wesley Lake, Asbury Park / Ocean Grove, New Jersey. {context}

Return ONLY a JSON array, one object per bird or homogeneous group in the frame.
Empty array if no birds. Each object:

{{"species": str, "confidence": one of {conf},
  "count": int, "count_exact": bool,
  "age_class": "adult|juvenile|cygnet|immature-year-N|eclipse|breeding|unknown",
  "stratum": one of {strata},
  "surface": one of {surfaces},
  "activity": one of {acts},
  "associations": str,
  "features": {{"bill":str,"legs":str,"head":str,"breast_flank":str,
               "wing_tail":str,"asymmetries":str,"size":str}},
  "marks_checked": bool, "marks": str,
  "tier": "A|B|C|D", "individual_id": str, "notes": str}}

THE CORE COUNT (PROTOCOL.md 5b). The lake's headline number counts birds ON THE
LAKE SURFACE and nothing else. Do not decide this yourself -- it follows from the
stratum you pick, so pick the stratum carefully:

  open_water     floating on the water                        -> counted
  shallows       standing IN the water, on the bottom (waders) -> counted
  island_or_mat  on a floating island                          -> counted
  shoreline_edge on the bank at the waterline, on GROUND       -> noted only
  bank_vegetation / overhanging_branch / in_flight             -> noted only
  man_made_perch dock, railing, pedal boat, pipe               -> noted only

A heron standing in the water is `shallows` and counts. A mallard standing on the
grass at the water's edge is `shoreline_edge` and does not. The distinction is
what the bird is supported by, not how close to the lake it is. Birds that are
only noted still get a full record -- they are observations, just not census rows.

SURFACES. Every counted bird is on a named surface. Open water is `open_water`.
Each floating island is its own surface with an ID from the registry in
geography.md, told apart by appearance, listed here with its signature:

{surface_notes}

If the bird is on a mat but you cannot tell WHICH mat, write `MAT-unassigned`.
Never guess a mat ID, and never use an unresolved one -- an unresolved mat may
not be a separate mat at all.

Rules, which override any instinct to be helpful:
- Write "not visible" in a feature rather than guessing it.
- tier D unless there is a durable hard mark (band, collar, tag, permanent injury,
  bill deformity, leucistic patch, entangled tackle) -> A, or a known territorial
  individual -> B, or a tracked cohort -> C. NEVER give a tier D bird an individual_id.
- If the bird is too small or distant to identify, say so: species "unknown",
  confidence "unknown". Do not produce a plausible species name.
- marks_checked true only if you actually examined legs/neck/bill at usable
  resolution. "Legs cleanly resolved, unbanded" is a real observation; "not
  visible" is not.
- Prefer "possible" over "probable" when uncertain. Do not round up."""

def build_prompt(path, context=''):
    try:
        import surfaces
        notes = '\n'.join(f"  {m['id']}  {m['signature']}"
                          for m in surfaces.registry() if m['confirmed'])
        avail = surfaces.assignable()
    except Exception:
        notes, avail = '  (registry unavailable — use MAT-unassigned)', \
                       [OPEN_WATER_SURFACE, UNASSIGNED_MAT]
    return PROMPT.format(path=path, context=context, conf=CONFIDENCE,
                         strata=STRATA, acts=ACTIVITIES,
                         surfaces=avail, surface_notes=notes)
