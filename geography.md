# Wesley Lake — Geography

Established from GPS on the 2026-09-20 transect. Revise as evidence accumulates.
Never harden an inferred position into a stated fact.

## Extent

**The lake has a real outline now.** Source: Geno, 2026-09-20, from Google Maps —
an 11-point perimeter clockwise from the western head at Railroad Avenue, along
the Asbury Park shore, round the east end at Ocean Avenue where it meets the
boardwalk flume, and back along Ocean Grove. It lives in `pipeline/lake.py` and
the geofence is now measured as **distance from the water**, not membership of a
bounding box.

That replaces an observed-extent box which had been widened twice, both times
after a confirmed on-lake photo fell outside it — because it described where the
photographer had stood rather than where the water is.

Roughly **1130 m east–west and 122 m north–south** as given — but see below: the
western head is short by at least 215 m, and correcting it brings the length to
1346 m (0.84 miles), which matches Geno's own "about 0.8 miles" where the
outline alone (0.70 miles) does not.

### SETTLED — the lake's western end is at ≈−74.0128, not −74.01021

A dedicated west-end survey on **2026-09-21** (43 photos in 8 minutes,
−74.01282 to −74.00979) closes this. Three independent things:

1. **A named sign.** IMG_3516 photographs a tiled parapet reading **WESLEY LAKE**,
   with a small plate **N28** above it, at −74.01266. Not an inference from
   appearance — the lake's own name on its own structure, 215 m west of the
   supplied head.
2. **A physical terminus.** IMG_3519 and IMG_3520 (−74.01283, the westernmost
   frames ever taken) show **steel-mesh and chain-link trash racks across a
   channel** and a concrete culvert opening beneath a bridge parapet. That is
   where the lake ends and drains. Floating litter is caught against the screens.
3. **Length.** The supplied outline gives 1131 m (0.70 mi). Extending west to the
   terminus gives **1346 m (0.84 mi)**, which matches Geno's own "about 0.8
   miles"; the outline alone does not.

Earlier evidence (16 photos on 6 dates, 2026-03-10 through 2026-09-10, all showing
open water extending away from the camera) pointed the same way at ~90%. With a
named sign and a terminus structure this is no longer an inference.

**The supplied western head at −74.01021 is short by roughly 260 m.** It is
probably the Main Street / Route 71 area rather than the true head.

### The outline and the archive contradict each other — a tilt, not an offset

| | photos sit |
|---|---|
| −74.013 … −74.010 (west) | 34–78 m **south** of the lake |
| −74.009 … −74.007 (Main St) | **on the water**, within 4–21 m |
| −74.006 … −74.001 (east) | 65–110 m **north** of the lake |

A constant GPS error cannot produce that, and neither can a constant map error.
A uniform latitude shift does not fix it either — the best one (+37 m) barely
improves anything, because moving north helps the east and hurts the west.

**A tilt fixes it almost exactly.** Holding the western head and raising the
eastern end:

| | on the water | median distance | worst |
|---|---|---|---|
| outline as supplied | 41 / 219 | 40 m | 160 m |
| outline tilted (−27 m west, **+258 m east**) | 70 / 219 | **6 m** | **45 m** |

A median of 6 m means the photographs essentially trace the lake. Two free
parameters on a 122 m strip is not a hard fit, so do not treat this as proof —
but it is a very good one.

### The dock IS photographed — and it does not contradict Google

IMG_3475 and IMG_3476 (2026-09-20, 15:10) clearly show the swan/animal pedal
boats lined along the Asbury bank, with the fountain aerator in frame. Their fix
is **40.21617 / −74.00576** — 224 m west-north-west of Google's dock coordinate.

**That is perfectly consistent.** A landmark 224 m away across a lake is an
ordinary thing to photograph. No conflict here at all.

### Where Claude overreached

The "168 m contradiction" reported earlier came from reading Geno's *"I was near
the pedal boats dock"* as *"I was at the dock"*, and pinning it to the 15:00–15:01
raft frames at 40.21741 / −74.00288. 168 m is about two blocks — entirely
reasonable as a verbal answer to "where were you?", and not the precise fix
Claude treated it as. **That leg is withdrawn too.**

What survives is narrower and still unexplained: at longitude −74.0029 the photos
sit 110–160 m north of where this outline puts the **north shore**, while §5a's
resolution formula puts the birds in those frames at 13–23 m. Standing 160 m
inland and photographing a bird at 13 m is not possible. Either the outline's
north shore runs further north there than given, or something about those fixes
is wrong.

### Where this rests — and why it is not blocking

Claude has now had to withdraw **two** supporting arguments here (a misremembered
landmark, and an over-literal reading of "near"), which is a fair signal that the
remaining analysis is being pushed past what the data can carry. The honest
summary:

- **Longitudes agree** between the archive and every supplied coordinate.
- **Latitudes disagree, increasingly toward the east**, in a way no constant
  offset explains and a tilt fits well (median 6 m vs 40 m).
- Claude's confidence that the photographs are right: **~65%**, down from 70%,
  because two of the three original legs are gone.

**None of this blocks anything.** The geofence admits all 219 photographs and
rejects the six genuinely off-lake ones. The pending work — the log, the
unphotographed eastern third, the bare-season mat survey — does not depend on
resolving the tilt. It should be settled opportunistically, not chased.

The cheapest settling move, if it ever matters: on the next walk, stand at the
spot the east-end raft was photographed from and note the cross street. That
converts a 160 m argument into a street name.

## Crossings

**Three.** Mattison Avenue, Heck Street / Embury Avenue, and Pilgrim Pathway.
*Source: Geno, 2026-09-20.*

Main Street / Route 71 and Ocean Avenue carry roads at the **western and eastern
ends** of the lake and do not span it. An earlier version of this file briefly
listed five crossings — that was Claude taking a list of named spans and assuming
they all crossed the water. `PROTOCOL.md` §0 said three all along and was right.

### The three crossings, west to east

| Crossing | Longitude (supplied, approximate) | Type |
|---|---|---|
| **Mattison Avenue** | −74.00480 | |
| **Heck Street / Embury Avenue** | −74.00195 | dedicated footbridge |
| **Pilgrim Pathway** | −73.99975 | dedicated footbridge, near Founder's Park |

### End features — not crossings

| | Longitude | |
|---|---|---|
| Railroad Avenue | −74.01021 | western head |
| Main Street / Route 71 | −74.00845 | road at the western end |
| Ocean Avenue | −73.99690 | road at the eastern end, at the boardwalk flume |

### Matching A, B and C — partly resolved

| photo-derived | reading |
|---|---|
| **A** ~−74.0058, **confirmed** — Geno stood on the deck, 15:08–15:10 on 2026-09-20 | Nearest crossing by longitude is **Mattison Avenue**, 85 m. Best candidate, not confirmed. |
| **B** — "looking back east from the western third, a second arch span appears behind Crossing A" | **Still likely real, and the reason has changed.** If A is Mattison, then looking east past it you would see Heck St / Embury and Pilgrim Pathway behind it. B is probably one of those. The "~−74.008" in the old table was **the photographer's position, not the bridge's** — a documentation bug, since a span *behind* A viewed from the west must be *east* of A. |
| **C** ~−74.0099, "probable" | **Probably not a crossing at all.** It sits 25 m from the Railroad Avenue head and was described as an elevated, centred view west down a *narrower, wooded channel with parking lots on both banks* — which is what the lake's western head looks like. Most likely the Main Street / Route 71 bridge or the head itself. |

If C is the western end rather than a crossing, the segment scheme below needs
renumbering: S4 is currently defined as "Crossing C → west end", which would
collapse.

**Still the one question that settles it: which named bridge did Geno stand on?**
Concrete multi-arch, black wrought-iron railing with scroll brackets, granite
pillars and ornamental lamp posts, fountain aerator running just west, the
swan/animal pedal-boat dock on the Asbury bank close by, Ocean Grove Victorians
opposite. Name it and B and C follow.

## Segments

East → west from the ocean end, bounded by the **three real crossings**. Defined
by longitude only: it is the coordinate the archive and the supplied data agree
on everywhere, and a segment is a stretch of water, not a point. Held in
`pipeline/lake.py:SEGMENTS`; `observe.py` **derives** each record's segment from
the longitudes of the frames it cites, so no record carries a typed one.

| | bounds | stretch |
|---|---|---|
| **S1** | −73.99690 … −73.99975 | Ocean Ave end → Pilgrim Pathway |
| **S2** | −73.99975 … −74.00195 | Pilgrim Pathway → Heck St / Embury Ave |
| **S3** | −74.00195 … −74.00480 | Heck St / Embury Ave → Mattison Ave |
| **S4** | −74.00480 … −74.01021 | Mattison Ave → Railroad Ave, the western head |
| **S5** | −74.01021 … −74.01283 | **real lake**, past the supplied head, to the terminus at the trash racks |

### What the renumbering exposed

The old scheme was bounded by photo-inferred crossings and stopped at −74.0029,
leaving 510 m of the eastern lake in no segment at all. Reassigning all 71
records by longitude gives:

| | core sightings | visits |
|---|---|---|
| **S1** | **none** | **never photographed** |
| **S2** | **none** | 2 visits (2025-06-10, 2025-10-20), both birdless |
| S3 | Mute Swan 12, Large gull sp. 5, Mallard 2, Duck sp. 2 |
| S4 | Mute Swan 50, Canada Goose 30, Cormorant 10, Mallard 9, unid 3, Gull sp. 1, Great Blue Heron 1 |
| S5 | Mallard 6, Canada Goose 6, Mute Swan 5, unid 1 |

**The two eastern segments hold no birds at all.** S1 has never been
photographed. S2 has been visited exactly twice — both 2025 dates, at the far
east end, and both recorded no birds. So the eastern third is not merely
under-sampled, it is **two birdless glances and a blank**. Every species
proportion in this project is effectively an S3–S5 proportion.

The unphotographed stretch is the 363 m from −74.00119 (the easternmost photo
ever taken) east to the Ocean Avenue end — all of S1 and most of S2.

**S4 holds most of the record** and is also the longest segment (~450 m). Some of
its dominance is just length; do not read it as habitat preference without
normalising.

**S5 is real lake**, and now has a real western bound: the terminus at
−74.01283, confirmed by the WESLEY LAKE sign and the trash racks. It is a
~220 m stretch and it is well used — 22 of the 43 frames from the 2026-09-21
survey fall in it, including the dock that held six mallards. Keep it as its own
segment; it is not an artefact and not a remainder.

## Floating islands

Multiple planted floating vegetation mats, **not one**. Rectangular base, planted
with what appears to be rose mallow / hibiscus plus sedges.

**They are a public works project** — deliberately installed and publicly managed.
*Source: Geno, 2026-09-20.* That settles "engineered, not accumulated debris," and
the March/April photos agree: the mats overwinter as bare woody clumps on the same
base and releaf, so the plantings are perennial and intended.

What is **still open** is their *purpose*. Floating treatment wetlands are installed
for nutrient uptake, but a public works project could equally be buying habitat,
shoreline aesthetics, or algae shading. "Nutrient treatment" remains an inference
(~70%). This is now a tractable question with a named owner rather than a guess:
the Wesley Lake Commission or the municipality will have the installation record,
the count, and the design intent. Ask, rather than squinting at photographs.

**They move.** They are anchored, but loosely enough to drift and swing around the
lake within some range. *Source: Geno, 2026-09-20.* Two consequences, and they are
severe:

- **Position is not an identity.** Not "we cannot measure it" — it genuinely is not
  a property of the mat. A fix on a mat dates as fast as the weather. Never write a
  mat's coordinates, and never identify a mat by where it was.
- **Position is not even a search hint across dates.** "The mat near Crossing A" is
  a statement about one afternoon. A mat's *neighbours* change too, so relative
  position is no better.

### Registry

Mats are identified by **appearance only**. Because they move and because the
planting is deciduous, a signature has to be split by what it survives:

- **Durable mark** — survives both winter and movement. This is a mat's equivalent
  of PROTOCOL.md §6 Tier A: a structural, non-seasonal, non-positional feature.
- **Seasonal / positional cues** — real, useful within a season or a single walk,
  and worthless outside it. Tier B/C at best. Never treat one as proof of identity.

| ID | Status | Durable mark | Seasonal / positional cues | Evidence |
|----|--------|--------------|----------------------------|----------|
| **MAT-01** | **Confirmed**, across dates | **A substantial dark log or timber lying across the base**, projecting well clear of the planting. Structural and non-seasonal. Matched on **three** dates: IMG_3185 (09-08), IMG_3446 (09-19), IMG_3461 (09-20) | Rose-mallow / hibiscus in open pink flower (summer) | IMG_3185 (2026-09-08); IMG_3446 (2026-09-19); IMG_3459, 3461, 3462, 3465 (2026-09-20) |
| **MAT-02** | **Confirmed** *within 2026-09-20* | **Not yet photographed at the waterline** — see below; the base carries one | Bright-green strap-leaved sedge / iris skirt round a central shrub. The 06-17 close views may be this mat — untested | IMG_3469, 3470, 3471, 3472 |
| **MAT-03** | **Confirmed** *within 2026-09-20* | **Not yet photographed at the waterline** | Tall dense leafy shrub, dark seed heads, reed-like stems, no flowers, no skirt | IMG_3479, 3480, 3481, 3483 |
| **MAT-04** | **Confirmed** *within 2026-03/04* | **Not yet photographed at the waterline** — though the bare March/April frames come closest | Bare multi-stemmed woody clump; dark coir/geotextile base; was lying against the Asbury bulkhead near the feeder station. **The mooring position is a cue, not a mark — it can drift** | IMG_1128, 1129 (2026-04-27); IMG_0722 (2026-03-30) |
| *MAT-?a* | **Unresolved** | — | Dense rounded shrub, no sedges, no flowers, small in frame | IMG_3466 |
| *MAT-?b* | **Unresolved** | — | Low spreading habit, reddish/pink flowers, sedges present, at distance | IMG_3473, 3474, 3477 |

### The base is manufactured, and that is where identity lives

**Corrected 2026-09-20.** An earlier version of this section said only MAT-01 had
a durable mark. That was a failure of looking, not an absence of marks: it was
written from summer frames, where foliage hides everything structural.

Close views of the base (IMG_2187, 2026-06-17) show a manufactured module:

- **Straight bevelled edges and defined corners** — a rectangular float, not an
  organic clump. Outline and proportions are measurable.
- **Round planting ports** cut through the surface. Countable, and their
  arrangement should differ between modules.
- **At least one artificial teal/turquoise element** standing proud of the
  surface — a tie, cable, stake or tag. Worth a deliberate close photo: this is
  the nearest thing to an asset marking seen so far.
- Heavy guano staining, which is itself a use signal.

None of that is seasonal and none of it is positional. It is the mat equivalent
of a Tier A hard mark, and it is available on **every** mat — it simply has to be
photographed at the waterline rather than from across the lake.

### Two ways identity chains, and what each can and cannot do

**1. A durable mark, from a close view.** MAT-01's log is the worked example:
the same timber, with birds perched on it, across three dates — IMG_3185
(09-08), IMG_3446 (09-19) and IMG_3461 (09-20). The 09-19 frame is the cleanest
demonstration: at ~90 m no flowers were resolvable and the position was different,
yet the log identified the mat outright. A cross-date match on structure, with
foliage and position contributing nothing. Base outline, port count and the teal element should do the same job
for the other mats once someone photographs them.

**2. Continuity across the year's series.** The record is denser than it looked:

| | state | close views |
|---|---|---|
| 2026-03-30 | bare woody stems, two mats visible | IMG_0721, 0727 |
| 2026-04-27 | bare, swan nest | IMG_1128, 1129 |
| 2026-06-17 | leafed out, **base clearly visible** | IMG_2186, 2187 |
| 2026-08-15 | full flower, two mats adjacent | IMG_2880–2883 |
| 2026-09-08 | full, MAT-01's log readable | IMG_3185 |
| 2026-09-20 | full, in flower | IMG_3459–3483 |

Steps of a few weeks mean change between consecutive visits is small, so a mat
can be followed forward through the year.

**But growth stage dates a photograph; it does not name a mat.** Every mat leafs
out on the same schedule, so leafiness distinguishes April from August, never
MAT-02 from MAT-03. Continuity only chains identity when each visit also
distinguishes the mats *from each other* — and because they drift, that has to be
appearance, never position. Coverage is also opportunistic: a mat not photographed
on a visit breaks its own chain, and nothing says every mat was in frame.

### Winter is the survey window

The bare season is not the problem it first appeared — it is the best time of year
to do this work. With the planting gone the base outline, port pattern, stem
count, stem arrangement and any hardware are all exposed, and a single walk in
January or February photographing each mat at the waterline would give the whole
registry durable identities at once. That is worth more than any number of
summer photographs from the bank.

### Bird use — beyond roosting

MAT-04 held a **mute swan nest on 2026-04-27**, two adults present, one sitting.
The mats are a **nesting** substrate, not only a roost, and this is the likely
origin of the 2026 brood of four. Claude's read from two frames; not confirmed by
Geno and not in the log.

That a nest sat on a mat that drifts is worth a thought in its own right.

## Water-quality stations

Fixed points photographed the same way every visit, so that what is in one
photograph can be compared with the next. PROTOCOL.md §3a. Parsed by
`pipeline/water.py`.

**CORRECTED 2026-09-21 by an exhaustive sweep.** An earlier reading of ~80
sampled frames concluded this lake "photographs clean". A frame-by-frame pass of
all 262 photographs found otherwise: a dumped drum, a floating carcass, vivid
green floating patches, a dead fish on a dock, and water that is strongly
ochre-brown on several dates. **The sample missed all of it**, because it was
drawn from montages built for bird work and therefore biased toward frames with
birds in them. The lake is not visibly polluted, but it is not clean either.

Six things were found across 31 dates: a **dumped drum** (2026-03-25), a
**floating carcass** (08-11), **vivid green floating patches** (08-12), a **dead
fish** on the dock (09-17, confirming log Entry 2), **strongly ochre-brown
water** on 07-09, 08-15, 09-04, 09-10 and 09-20, and a **litter and debris mat**
at the western trash racks (09-21).

Station WQ-1 remains the right place for a *series*, because it is the one point
everything floating must pass. But roving observations clearly matter too, which
is what `LAKE-WIDE` is for.

| ID | Where | Why here | What it gives |
|----|-------|----------|---------------|
| **LAKE-WIDE** | not a place — the whole lake, from wherever it was seen | Some properties are not local. Ice covers the lake or it does not; you do not need to be at a station to see it | **ice cover only.** Everything else must be `not_assessable`: without fixed framing there is nothing to compare |
| **WQ-1** | Western terminus, ≈40.2145 / −74.0128 — the trash racks and culvert below the WESLEY LAKE parapet | Every floating thing in the lake ends up against these screens. It integrates the whole lake at one point, which no open-water view can do | discrete litter count; organic debris load against the mesh; **water level against the galvanised posts and concrete sill**, which are a free fixed gauge; ice |

**Two frames per visit**: one wide showing the whole rack, sill and posts; one
closer on the waterline. That is the entire protocol.

**WQ-1 has been photographed once**, on 2026-09-21 (IMG_3519, IMG_3520). It
becomes a series on the second visit and means something by the fourth.

**Do not file a roving observation under WQ-1.** If the rack was not in frame,
the station is `LAKE-WIDE` and only ice is recordable. Mixing the two would put
incomparable readings in one series, which is the exact failure a fixed station
exists to prevent.

## Other fixed features
- Fountain aerator just west of Crossing A.
- Swan/animal pedal-boat dock, Asbury bank near Crossing A.
- Garden bird feeder pole and bird bath on the Asbury bank. **Position uncertain —
  the recorded fix is bad.** Entry 4 gives ~40.2158 / −74.0077, which is IMG_3488's
  own GPS, and that fix is stale: IMG_3487→3488 implies 3.1 m/s and 3488→3489
  implies 15.6 m/s, while 3487→3489 *skipping it* gives 0.7 m/s — a normal walking
  pace. IMG_3488 is a single-frame stop between two multi-frame stops, the classic
  signature of a phone waking up and reporting its last known position before
  reacquiring. The feeder is somewhere on the Asbury bank near 40.2155 / −74.0070;
  it has not been fixed properly. Small landbirds present there — the only
  non-waterbird habitat noted so far.
- Steel sheet-piling bulkhead along much of the Asbury bank (and the reason phone
  compass headings are unreliable here).
- **Western terminus**, ≈−74.0128: steel-mesh and chain-link trash racks across
  the channel, a concrete culvert beneath a bridge parapet, and a tiled **WESLEY
  LAKE** sign with an **N28** plate on the parapet. IMG_3516, 3519, 3520
  (2026-09-21). Litter visibly caught at the screens — a water-quality
  observation, and the obvious place to look for floating debris load.
- **Low wooden dock on the Ocean Grove bank at ≈−74.0103**, west of the supplied
  head. Held six mallards on 2026-09-21. Distinct from the Asbury Park pedal-boat
  dock at −74.00315; Claude briefly mistook the ducks on it for pedal boats.

## GPS quality — good, with one systematic fault

Within a burst the fixes are excellent: on 2026-08-11 sixteen frames over three
minutes hold position to 1–2 m. The lake's GPS is not noisy.

**But the first frame after the phone wakes up often carries a stale fix.**
9 of 170 consecutive pairs across the whole archive imply more than 3 m/s — a
brisk walk — and every one of them is a first-of-burst frame, not a run of drift.
Worst cases: IMG_2831→2832 (79 m in 4 s), IMG_0577→0578 (34 m in 2 s),
IMG_3488→3489 (62 m in 4 s).

Consequences:
- **A stale fix invents a stop.** IMG_3488 became its own single-frame stop on
  2026-09-20 purely because of this, and Entry 4 then read it as a separate
  location.
- **Never take a position from a single-frame stop** without checking the frames
  either side. If dropping the frame makes the walk continuous, the fix is bad.
- The test is cheap and should be automated: flag any consecutive pair implying
  more than ~3 m/s.
