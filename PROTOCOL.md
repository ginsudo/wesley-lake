# Wesley Lake — Bird Observation Protocol

Durable working document. The claude.ai Project Instructions point here; this file
holds the actual method. Edit this file to change how the work is done.

Last revised: 2026-09-20 (§5b added: core count and surfaces)

---

## 0. Scope

The Wesley Lake project covers several connected interests: water quality, wildlife
habitat, and tech-driven monitoring for the lake. Bird observation is one thread of
it, and is also simply enjoyable birdwatching. Treat it as both data collection and
pleasure — the record should be rigorous, the tone should not be grim.

**What kind of water body this is, because it governs everything below.**
Wesley Lake terminates at Ocean Avenue at a **flume**, and has a culvert and
trash racks at its western head. That is the signature of a NJ-shore **coastal
lagoon** — an impounded former tidal creek behind the barrier beach, in the same
family as Deal, Sunset and Fletcher Lakes — not a freshwater pond. Three
consequences:

- **Water level may be tidal.** If there is exchange through the flume, level
  varies over hours. Every level reading therefore carries a tide stage
  (§3a); without one it is not comparable to anything.
- **The floating treatment mats are themselves a water-quality datum.** A public
  works body does not install them in a healthy lake. They are a standard
  eutrophication intervention, which means somebody has already diagnosed a
  nutrient problem here. Treat them as evidence, not just as bird furniture.
- **Winter is the season this record is missing.** On NJ coastal lagoons the
  interesting waterfowl are the winter ones — Brant, Bufflehead, scaup, Ruddy
  Duck, Red-breasted Merganser, American Coot, Great Cormorant, large gull
  flocks. See §9 on effort bias.

Wesley Lake is the boundary water between Asbury Park (north shore) and Ocean Grove
(south shore), Monmouth County, NJ. It is small and walkable end to end. Geno gives it as about 0.8 miles
(≈1290 m) along its east–west axis; a supplied outline makes it ≈1130 m, so
call it 1.1–1.3 km. It has **three crossings** — Mattison Avenue, Heck Street /
Embury Avenue, and Pilgrim Pathway. Main Street / Route 71 and Ocean Avenue are
at the western and eastern *ends* and do not span the lake. See `geography.md`.

---

## 1. Trigger and ingest

Geno downloads a Google Photos zip to the project root on the MacBook Air —
usually whenever he happens to be at the laptop and remembers. Then he says
something like "go check for new photos."

That means: run the local pipeline first, then review only what needs reviewing.

    python3 pipeline/run.py

It unzips, reads EXIF, files each photo into `photos/YYYY-MM-DD/` by its own
`DateTimeOriginal`, geofences (off-lake goes to `photos/_off-lake/`), clusters
each date into stops, builds `work/<date>/stop*.jpg` contact sheets, writes
`analysis/session-index.md`, and archives the zip. Measured at 45 s for 153
photos. It is idempotent — re-running is always safe.

Claude runs this via the device shell; Geno does not have to remember the
command. Then Claude reads `analysis/session-index.md` and the new contact
sheets, and goes to §4.

Note: deletion is disabled in connected folders. Move files, don't delete them.

## 2. Tooling

All processing is local, on the Air. `pillow` + `pillow-heif` are the only
dependencies; HEIC is the native iPhone format and plain Pillow cannot open it
without the plugin. `exiftool` is not installed and is not needed — `pipeline/exif.py`
is validated against it and matches exactly.

The one thing that cannot happen locally: Claude cannot *see* an image from the
device shell. Vision requires the file staged into the cloud container. So stage
only the specific frames that need looking at — contact sheets first, then the
native-resolution crops of individual birds. Never stage a whole batch.

This is also the cost model. Running scripts is free; looking at images is not.
A normal outing of 5–15 photos is a handful of image reads. The expensive case is
a large backlog, which is why the pipeline pre-filters.

## 3. Geofence

Observed lake extent (GPS, 153 photos Mar–Sep 2026): lat 40.21451–40.21741,
lon −74.01244 to −74.00288. The west bound was widened on 2026-09-20 after March
photos at −74.0124 fell outside an earlier, too-narrow box.

- **ON_LAKE**: inside lat 40.2140–40.2180 AND lon −74.0135 to −74.0025
- **NEAR**: within ~200 m of that box
- **OFF**: otherwise

Widen the box if a confirmed on-lake fix ever falls outside it. Never use a
single-point radius — an early version of these instructions did, with a 150 m
radius on one mid-lake point, and it classified the entire Carousel end as
off-lake.

If a photo has no GPS: say so plainly, ask Geno once for date and location, and
record `location_source: user` or `unknown`. Never infer a location silently.

If ON_LAKE or NEAR: check for birds. If none, record it as a no-bird lake
observation anyway — water clarity, algae, ice, crowding, and landmark evidence all
matter. If OFF and no birds, say so briefly and record nothing.

## 3a. Water quality — only what a photograph can carry

§0 makes water quality one of this project's threads, and §3 has always said to
record clarity, algae and ice. It was never done: for 31 dates the schema had no
field for any of it. This section defines what is actually recordable, and is
deliberately narrow.

**Start from the evidence.** All 262 photographs have now been swept frame by
frame. The lake is not visibly polluted, but it is **not clean either**: one
dumped drum, one floating carcass, vivid green floating patches on one date, a
dead fish on a dock, and water that runs strongly ochre-brown on five dates.

An earlier sample of ~80 frames concluded the lake photographed clean and
**missed every one of those**. The sample came from montages built for bird
work, so it leaned toward frames with birds in them. Sample a biased set and you
will confirm whatever it was biased toward. So the useful question is not "how bad does
the open water look" but **"how much collects at the one point everything
floating has to pass"** — the trash racks at the western terminus, station WQ-1
in `geography.md`.

### Fixed station, two frames, every visit that reaches it

One wide frame showing the whole rack, sill and posts; one closer on the
waterline. Same spot, same framing. Without fixed framing there is nothing to
compare, which is the same reason the bird side wants a fixed transect.

### What is recorded

| field | values |
|---|---|
| `surface_state` | glassy / rippled / wind_whipped / frozen / not_assessable |
| `ice_cover` | none / partial / complete / not_assessable |
| `organic_load` | clear / scattered / banded_below_rail / packed_to_rail / overtopping / not_assessable |
| `water_level` | below_sill / at_sill / mid_posts / at_rail / above_rail / not_assessable |
| `marginal_vegetation` | absent / sparse / fringing / dense / not_assessable |
| `litter_count` + `litter_types` | discrete visible items; plastic_film / bottle_can / other |
| `notable` | free text, and expected to be empty |

`not_assessable` carries the weight "not visible" carries in a feature string
(§5a): a real answer, and not the same thing as a zero.

**`surface_state` is a quality flag, not data about the lake.** It records
whether the frame supports assessment at all — wind-whipped water hides floating
litter. `water.py:validate` refuses an exact litter count taken through a
surface that cannot support one.

**The rack is also a free gauge.** Its galvanised posts and concrete sill are
fixed structures at a fixed point, so water height reads off them between visits
without anyone installing anything.

**Log "nothing unusual" explicitly**, the way an empty mat is logged. A clean
lake recorded is data; a clean lake unrecorded is silence.

### What is deliberately NOT recorded, and why

- **Measured colour, clarity, turbidity.** A patch of this lake reads RGB
  185,181,169 in sun and 89,95,96 in shade — the variance is illumination, with
  iPhone HDR on top, and depth is not visible in a photograph. A number from
  those pixels would be invented precision (§9). Clarity needs a **Secchi disk**,
  not a better algorithm — about $30, and the only instrument that would turn
  this thread into measurement.
- **But JUDGED colour is recordable, under one condition.** The sweep overturned
  the earlier blanket exclusion. Under a **clear blue sky** a merely reflective
  surface reads blue, so water that reads ochre-brown under blue sky is brown.
  That is a categorical judgement by eye, gated on `sky == 'clear'`, and
  `water.py:validate` enforces the gate. It is not a measurement and must never
  be turned into one. Cause is not determinable from a photograph — sediment,
  tannin and an algal tint all look the same.
- **An algae scale.** There is one candidate observation (2026-08-12, vivid green
  floating patches, most consistent with duckweed or filamentous algae) — not
  enough to calibrate categories against, and the identification is uncertain at
  that range. Keep it in `notable` until there is more. Nothing like a bloom has
  been seen.
- Anything chemical or biological. Not a photographic question.

### Status

WQ-1 has been photographed **once**, on 2026-09-21. This is a protocol with one
observation behind it. It becomes a series on the second visit and means
something by the fourth.

## 4. Analysis method

Two passes. This matters for cost and for accuracy:

**Pass 1 — overview.** Build per-stop contact sheets (group photos into stops by
clustering on GPS distance >35 m or time gap >75 s). Read the sheets to map the
walk, locate landmarks, and find which frames contain birds. A contact sheet costs
about what a single image costs, so each photo in it is at low effective
resolution — fine for "where was this," useless for identification.

**Pass 2 — identification.** Crop each bird at native resolution and read the crops.
This is where species, age class, and any hard marks become visible. Do not attempt
an ID from a contact sheet.

Also reconstruct the track: cumulative distance, stop sequence, direction of travel.
A dated walk is one observation event even if it arrives as several batches.

## 5. What to record, per bird or group, per photo

- species (+ confidence: certain / probable / possible / unknown)
- count (exact if countable, `~N` if estimated — say which)
- age / plumage class (adult / juvenile / cygnet / immature-year-N / eclipse / breeding)
- **stratum**: open_water | shallows | island_or_mat | shoreline_edge |
  bank_vegetation | overhanging_branch | in_flight |
  man_made_perch (dock/railing/pedal_boat/pipe)
- **census class** — `core` or `noted`. Derived from stratum, never chosen. §5b.
- **surface** — which surface the bird was on: `open_water`, or a mat ID from the
  registry in `geography.md`. Required for every core bird. §5b.
- **activity**: loafing | sleeping | preening | wing_drying | dabbling | diving |
  plunge_diving | stalking | gleaning | walking | aggression | courtship |
  brooding | flying_through | taking_off | landing
- **segment** (see `geography.md`) and **bank** (N = Asbury, S = Ocean Grove, mid)
- raw GPS alongside the segment — free, and it is what lets a mistake be caught later
- associations (what it was mixed in with)
- **feature string**, always, even for Tier D birds, in fixed order:
  `bill color/pattern | leg-foot color | head marks | breast/flank pattern |
  wing/tail marks | asymmetries or damage | relative size`
  Write "not visible" rather than guessing.
- **identity tier**, and an individual ID if Tier A or B

## 5a. Hard-mark check (do this on every identifiable bird)

Before writing the feature string, crop the legs, neck, bill and wing at native
resolution and look specifically for: metal or colored leg bands, neck collars,
wing or patagial tags, bill deformities, missing toes, drooping wings, leucistic
patches, entangled line or tackle.

Record the result either way. "Legs cleanly resolved, unbanded" is a real
observation; "not visible" is not. Say which one it is.

A mark found this way is a Tier A bird — open a record in `logs/individuals.md`.

Resolution on subject (iPhone main wide, frame width ~= 1.5 x distance):
`px_per_cm = image_width_px / (150 * distance_m)`. Need ~3-4 px to SEE a mark,
~15-20 px of character height to READ a band code. At ~20 m a collar's colour is
readable but its code is not; a code needs the bird inside ~10 m or a zoom frame.

Caution: iPhone processing reconstructs fine detail rather than merely filtering
noise. At extreme crop magnification part of what you are reading was synthesised
by the phone. Call a mark present or absent at that scale; do not read a pattern
out of a 4-pixel smudge.

## 5b. The core count — what the lake's number means

The headline count for a session is **birds on the surface of the lake**. Nothing
else. That is the number that goes in rollups, that gets compared month to month,
and that means something about the lake.

**Counted (`core`)** — the bird is on or in the lake:

| stratum | |
|---|---|
| `open_water` | floating on the water |
| `shallows` | standing *in* the water, supported by the bottom — waders |
| `island_or_mat` | on a floating island |

**Noted, not counted (`noted`)** — everything else:

| stratum | |
|---|---|
| `shoreline_edge` | on the bank at the waterline, on ground |
| `bank_vegetation` | in bankside planting |
| `overhanging_branch` | in a tree, even directly over the water |
| `in_flight` | flying over, through, or above |
| `man_made_perch` | dock, railing, pedal boat, pipe — all of them |

The test is **what the bird is supported by**, not how close to the lake it is. A
heron standing in 20 cm of water is `shallows` and counts. A mallard on the grass
a metre away is `shoreline_edge` and does not.

Two things this rule is not:

- **It is not a reason to record less.** Noted birds get the full record — species,
  features, hard-mark check, the lot. Birds on the ground right next to the lake
  are worth having, and birds in flight are worth having; they are simply a
  different number. The landbirds at the Asbury feeder station will be almost
  entirely `noted`, and that does not make them less interesting.
- **It is not a judgement call.** Census class follows from stratum by the table
  above. If a record's census class and stratum disagree, `schema.validate` says
  so and neither is silently changed. Pick the stratum honestly and the count
  takes care of itself.

Pedal boats are `noted` even though they float. That is a deliberate line: the
core count is the lake's own surface, and rental boats move, come and go
seasonally, and belong to the park rather than the water.

### Surfaces — each floating island is its own place

The lake's surfaces are **open water** and **each floating mat, individually**.
A mat is not scenery, it is a place that bird life is recorded against — the same
standing a segment has. `geography.md` holds the registry; every core bird names
its surface.

- A mat with **nothing on it** is a real observation. Record it. "MAT-02 empty,
  15:09" is data about roost preference; silence is not.
- If a bird is on a mat but you cannot tell **which** mat, write `MAT-unassigned`.
  Never guess an ID.
- Mats in the registry marked **unresolved** may be duplicates of a confirmed mat.
  Never log a bird onto one. Settle it with a deliberate photo first.
- **Mat identity is tiered, exactly as bird identity is (§6), and for the same
  reason.** The mats are a public works installation, but they *float* — anchored
  loosely enough to drift and swing around the lake — and the planting is
  deciduous. So:
  - **Durable mark** (the mat equivalent of Tier A): a structural, non-seasonal,
    non-positional feature. MAT-01's log is the only one found so far. A mat with
    a durable mark can be matched across dates and seasons.
  - **Within-season identity** (Tier B/C): flower colour, a sedge skirt, leaf
    habit, where it was lying that afternoon. Real for one walk or one season,
    **not** evidence of identity on another date.
  - **No identity** (Tier D): `MAT-unassigned`. Still the correct answer whenever
    the mat was only seen from across the lake.
- **The durable marks are on the base, not the planting.** Close views at the
  waterline show a manufactured module: straight bevelled edges, defined corners,
  countable round planting ports, and hardware. That is available on every mat —
  it just has to be photographed from close enough. A mat with "no durable mark"
  in the registry means nobody has taken that photograph yet, not that the mat
  lacks one.
- **Winter is the survey window, not the blind spot.** With the planting gone the
  base and its structure are fully exposed. One walk in the bare season,
  photographing each mat at the waterline, is worth more than a season of
  summer shots from the bank.
- **A dense series lets identity chain forward.** Visits a few weeks apart mean
  small changes between them, so a mat can be followed through the year. But
  **growth stage dates a photograph; it does not name a mat** — every mat leafs
  out on the same schedule, so leafiness separates April from August, never one
  mat from another. Chaining works only where each visit also tells the mats
  apart, and a mat missed on a visit breaks its own chain.
- **Do not inflate a cue into a mark.** Matching a September mat to a March mat on
  foliage is the same error as calling two mallards the same bird.
- **Position is not an identity, and not even a hint across dates.** Not "we cannot
  measure it" — a drifting mat genuinely has no fixed position to be identified by.
  Never write a mat's coordinates, and never write "the mat near Crossing A" as
  though it named one. A mat's neighbours move too.
- Record the **segment and bank as observed on the day**, per sighting. For a mat
  those are facts about that sighting, not properties of the mat.

## 6. Identity tiers — do not inflate these

- **Tier A (individual, durable):** leg band, neck collar, wing tag, permanent
  injury, bill deformity, leucistic/melanistic patch, entangled tackle. Assign an
  ID: SWAN-A01, CORM-A01, GBHE-A01. Record the mark verbatim.
- **Tier B (territorial, within-season):** one-bird or one-pair species with
  consistent site fidelity. The resident mute swan pair is Tier B. State the
  inference explicitly every time ("same stretch, same pair, assumed").
- **Tier C (cohort):** e.g. the 2026 cygnet brood (n=4). Track group size, growth,
  molt stage. Never split into individuals.
- **Tier D (unindividuated):** mallards, geese, gulls, flocks. Counts only. Never
  assign an individual ID. If asked whether two photos show the same bird, the
  correct answer is usually "unknowable."

Image similarity, embeddings and perceptual hashing match *photographs*, not
individuals — never use them as evidence of a repeat individual. The feature string
exists so that if a hard mark ever appears, past sightings become searchable
retroactively. It is not a live matching system.

## 7. Where things live

Everything durable lives in this folder. Nothing durable lives only in a chat.

```
Wesley Lake/
  PROTOCOL.md                     this file — the method
  geography.md                    crossings, segments, landmarks, floating islands
  logs/bird-log.md                the running sightings log, append-only
  logs/narrative.md               Geno's own journal, append-only, never summarized
  logs/individuals.md             Tier A and B catalog (create on first hard mark)
  logs/patterns.md                seasonal and daily rollups (update monthly)
  analysis/YYYY-MM-DD-*.md        per-session working analyses
  photos/YYYY-MM-DD/              originals, full resolution, EXIF intact
  archive/zips/                   processed source zips
```

Claude's memory keeps only a pointer to this folder plus the handful of facts that
must be available on surfaces where the folder is unreachable (phone, web). Memory
is not a second copy of the log — two copies drift.

## 8. Rollups (build from the log, not per photo)

Every rollup below is built from the **core count** (§5b) unless it says
otherwise. State which you used — a species total that quietly mixes flying birds
with rafting birds is not comparable to anything.

- **Species composition:** counts and proportions per species per month.
- **Segment use:** which species use which segments, by stratum.
- **Surface use:** per floating mat — which species, how often occupied, how many
  at once, and how often it was empty. Mats are the lake's main roost structure,
  so this is the closest thing to a habitat-quality series the project has. Keep
  `open_water` as its own surface in the same table.
- **Noted-only log:** birds in flight, on the banks, and on man-made perches,
  kept separate and never folded into the core series. Overflights especially —
  they say something about the lake's role as a corridor rather than a habitat.
- **Seasonal narrative:** arrival and departure, breeding, molt, brood survival,
  overwintering. Note phenology events with dates.
- **Daily narrative:** bin by dawn / morning / midday / afternoon / dusk and describe
  what is typically doing what, and where. Flag when a pattern rests on too few
  observations to mean anything.
- **Water-health crossover:** cormorant and heron activity indexes fish presence;
  large goose and gull concentrations index nutrient loading; abrupt avoidance of a
  stretch may index a bloom or fish kill. These are hypotheses, not findings.

## 9. Discipline rules

- Species IDs from photos are Claude's read, not Geno's confirmation. Mark them as
  such. Ask him to confirm anything that would be a first for the log.
- Distinguish "same photo re-counted" from "additive new birds." Ask when unsure.
- Never upgrade a count estimate into an exact number, or a "possible" ID into a
  "probable" one, on retelling.
- Never harden an inferred crossing position or an inferred feature into a stated
  fact. Keep confidence fields honest.
- Distant or small birds are often genuinely unidentifiable at the available
  resolution. Say "can't tell from this image" rather than producing a plausible
  species name.
- Give confabulation-risk odds on any specific claim made without a source.
- `GPSImgDirection` is recorded but unreliable at this lake — the banks are steel
  sheet piling, which distorts a phone magnetometer. Trust position, not heading.
- One walk is one observation event, however many upload batches it arrives in.
- **Know what season the record is biased toward.** As of 2026-09-21 this log
  holds 31 dates, of which **one** falls in November–February and that one was
  frozen. Every species proportion is a breeding-and-late-summer proportion.
  The nine species recorded are all year-round generalists; the winter visitors
  that define a NJ coastal lagoon are simply absent from the record, not from
  the lake. Do not read the species list as the lake's avifauna.
- **Mute Swan is non-native in New Jersey**, aggressive toward other waterfowl,
  and uproots submerged vegetation; NJDEP operates a control policy. The log
  follows the resident pair closely and warmly, which is right for a
  birdwatching record — but the water-quality thread and the bird thread are
  describing the same animal, and §8's rollups should say so rather than
  treating them as separate subjects.
