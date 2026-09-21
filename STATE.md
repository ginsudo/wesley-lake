# Wesley Lake — current state

Last updated 2026-09-20 (detector built; §5b core count and mat surfaces added; **the full archive is now in the log**). **A new Claude thread should read this first, then
`PROTOCOL.md`, then `CLAUDE.md`.** This file says where things stand; the others
say how the work is done.

---

## Where we are

262 on-lake photos over 31 dates (**Jun 2025** – Sep 2026), plus 6 in `photos/_off-lake/`,
are ingested, EXIF-indexed, geofenced, filed by date, and contact-sheeted.
(An earlier version of this file said 153 / 101 unlogged; the real backlog is
**147 photos over 26 dates**.) **Only 2026-09-20 has been analysed and logged.**

The deterministic pipeline is built. The model layer is built and swappable.
**The detector is built** and off by default.

## Done

- `pipeline/` — **one command does the whole machine half**:
  `python3 pipeline/run.py` → ingest, EXIF, geofence, stops, contact sheets,
  **bird detector sweep**, **water-band sheets**, then a printed to-do list of
  what still needs eyes. Idempotent.
  The pipeline splits MACHINE (deterministic, re-runnable) from EYES (species,
  counts, water judgements). `pipeline/status.py` reports the split per date.
- `pipeline/schema.py` — fixed observation record + a validator that enforces
  PROTOCOL rules rather than trusting the model (catches Tier D with an
  individual ID, Tier A without a mark, missing feature keys, and now a census
  class that contradicts its stratum or a mat ID that is not in the registry).
- **PROTOCOL.md §5b — the core count.** The lake's headline number is birds on
  the lake surface: `open_water`, `shallows` (waders standing in the water), and
  `island_or_mat`. Flying, bank, bankside vegetation, overhanging branch and all
  man-made perches (pedal boats included) are recorded fully but kept out of the
  count. Census class is derived from stratum, never chosen.
- **Each floating mat is a surface with an ID.** Registry in `geography.md`,
  parsed by `pipeline/surfaces.py` (header-driven, so the table can grow columns).
  Four confirmed, two unresolved sightings. An empty mat is a recorded
  observation. Mats are a **public works project** and they **drift**, so the
  registry separates durable marks from seasonal/positional cues.
- `pipeline/providers/yolox.py` + `pipeline/detect.py` — the detector. YOLOX-S
  (Apache-2.0, 34 MB ONNX), ONNX Runtime on CoreML+CPU, ~1.2 s per 24 MP frame.
  Sweeps overlapping native-resolution tiles, which is the whole point: with
  tiling off it finds 52 boxes in 17/52 frames instead of 229 in 51/52.
  Emits crops, §5a sub-crops and `analysis/<date>-candidates.json`.
  Measured 8/8 group recall against Entry 4. Off by default:
  `config.json` → `"detector": "yolox"`.
- `pipeline/census.py` — rolls records into core / noted / per-surface / per-segment totals.
- **PROTOCOL.md §3a + `pipeline/water.py` — water quality, finally tracked.**
  §0 made it a thread and §3 asked for it; for 31 dates the schema had no field
  and it appeared 5 times as incidental free text. Now a fixed station (WQ-1,
  the western trash racks) with categorical fields and one real observation.
  No colour/clarity/turbidity — unmeasurable from these photos.
- `pipeline/observe.py` — the pass-2 writer. Derives stop, event, census_class and
  detection provenance rather than accepting them typed.
- **Detector precision collapses on snow and ice** (2026-01-31): 179 detections
  at >=0.30, essentially all snow lumps, scoring up to 0.78. Recall was measured
  on three dates and found no misses — all three were liquid water. See
  `analysis/2026-01-31-detector-failure.md`. Winter dates must be counted by eye.
- `pipeline/test_pipeline.py` — 35 checks over the above.
- `pipeline/providers/` — `claude_cli` (default), `claude_api`, `local_vlm`,
  `manual`. Swap via `pipeline/config.json`.
- `logs/bird-log.md` Entry 4 — the 2026-09-20 transect, fully analysed from
  full-resolution originals.
- `geography.md` — Crossing A confirmed; segments; floating mats.

## Pending, ranked

**The archive is logged.** `logs/bird-log.md` Entry 5 backfills all 30 dates;
Entry 6 appends corrections to Entry 4. `logs/individuals.md` and
`logs/patterns.md` now exist. What is left is mostly field work.

1. **Walk the eastern third.** 363 m from −74.00119 east to Ocean Avenue has
   never been photographed — segment S1 not once, S2 twice and both birdless.
   It contains two of the three crossings. Every species proportion in
   `logs/patterns.md` is an S3–S5 proportion until this is closed.
2. **A fixed transect.** The single most valuable change available to the
   water-quality thread. §8 wants goose and cormorant concentrations as indices;
   an index needs consistent effort and this record has none — 11 of 30 dates
   are one stop of 1–5 photos. One repeatable walk, same route, comparable time,
   even monthly.
3. **Photograph WQ-1 on every walk that reaches the west end.** Two frames:
   one wide on the rack, sill and posts; one closer on the waterline. n=1 today;
   it becomes a series on the second visit. Consider a **Secchi disk** (~$30) —
   the only instrument that would turn any of this into a measurement.
4. **Ask the Wesley Lake Commission**: installation record for the mats, how
   many, how anchored, what for — and **whether they are lifted for winter**,
   which decides whether item 4 is possible at all.
4. **One bare-season walk photographing every mat at the waterline.** The base is
   a manufactured module — bevelled edges, corners, countable planting ports,
   hardware, a teal element on at least one. It would give every mat a durable
   identity in a single outing. Only MAT-01 has one now.
5. **Next winter: is the frozen lake used by birds?** Geno expects yes; the one
   winter visit found none. Do NOT use the detector (179 false positives, snow
   scoring to 0.78). Photograph dark shapes at 2x or closer, concentrate on
   wet-ice leads and open water, look for shadows and legs.
6. ~~**Re-do log Entries 2 and 3.**~~ **Done — log Entry 7.** Entry 2's dock
   cormorant is dated and fixed (IMG_3402, 10:05:04, match to metres) with a
   clean hard-mark negative. **Entry 3's ~26 additive geese STAND** — Claude
   drafted a correction down to 10 on the strength of the event grouping and was
   wrong: 3404 and 3405 are 9 s apart because Geno turned, and the frames show
   different water. Unreconcilable: most of Entry 2 is in chat-only photos never
   ingested, including the white wader, which is now probably unresolvable
   forever.
7. **Name Crossing A.** Geno stood on its deck 15:08–15:10 on 2026-09-20.
   Nearest crossing by longitude is Mattison Avenue (85 m). Naming it places
   B and C, and B is probably a real second span while C is probably the
   western end rather than a crossing.

## Open questions — do not harden these into facts

| Question | Status |
|---|---|
| Crossing B — real, or Crossing A's arches at an angle? | Unresolved. One deliberate photo settles it. |
| Are the floating mats engineered? | **Settled.** A public works project — Geno, 2026-09-20. March/April photos agree: they overwinter as bare woody clumps on the same base and releaf. |
| Are they *treatment* wetlands specifically? | Still ~70%. A public works project could be buying habitat, aesthetics or algae shading instead. Now a tractable question with an owner: the Commission or the municipality holds the installation record, count and design intent. |
| How many mats are there, and where? | Unknown. 4 confirmed, 2 unresolved sightings, none west of −74.0099 ever looked for. The installation record answers this outright; photo-inference will not, because the mats move. |
| Is the 2026-09-20 heron immature? | ~65%. Dark bill and crown, no plumes; overcast light can dull a yellow bill. |
| Gull species at the east end | Unresolved. Ring-billed vs Herring; no bill pattern readable. |
| Does `claude -p` bill under the Max subscription rather than metered API? | ~75%. Verify before relying on it. |
| The white wading bird of 2026-09-17 | Great Egret or Snowy Egret, a first either way. In chat-only photos that were never ingested; **probably unresolvable**. The clearest cost of photos arriving via chat rather than as originals. |
| What is the ochre-brown water? | Strongly brown on 5 of 31 dates, judged under clear sky so it is real colour, not reflection. Sediment, tannin or algal tint — **not determinable from a photograph**. A Secchi disk would be the cheapest next step. |
| Were the vivid green patches of 2026-08-12 algae? | Uncertain — duckweed, filamentous algae or floating litter all look alike at that range. The only algae-like observation in the archive. Photograph closely if it recurs. |
| Was the 2026-03-25 dumped drum ever removed? | Unknown; no later frame covers that spot. |
| The landbird feeder station on the Asbury bank (~40.2158/−74.0077) | Never deliberately visited. The log is otherwise all waterbirds. Note these will be almost entirely §5b `noted`, not core. |
| Are the mats present in deep winter, or lifted out? | Unresolved and it matters: 2026-01-31 shows none, but the lake is frozen under snow. If they are removed seasonally, the recommended bare-season waterline survey is impossible. Ask the Commission. |
| Does the lake freeze every winter, and for how long? | It freezes — 2026-01-31, bank to bank, confirmed. n=1, no series. |
| Do birds use the frozen lake? | **Geno expects yes; untested.** Nothing in the 2026-01-31 frames supports it — the 18 largest detections are each snow or ice at native resolution. Test next winter, and NOT with the detector (179 false positives, snow scoring to 0.78): photograph dark shapes at 2x or closer, concentrate on wet-ice leads and open water. |
| ~~Is the east-end brick building correctly named?~~ | **Closed.** It is the old **Carousel**, as the 2026-09-20 transect originally read it (flagged there at ~25% confabulation risk). The Asbury Park Casino is separate, slightly further east. Geno, 2026-09-20. |
| Outline vs archive: a latitude tilt | **Open but NOT blocking — do not chase it.** Longitudes agree everywhere; latitudes disagree increasingly eastward, and a tilt fits the photos to a median 6 m from the water. Claude has withdrawn two of its three supporting arguments here (a misremembered landmark, an over-literal reading of "near the dock") and is at ~65%. The geofence admits all 219 photos regardless. Settle it opportunistically: on the next walk, note the cross street where the east-end raft is photographed from. |
| Where exactly was Geno for the east-end raft? | Near the pedal-boat dock, per Geno — which at ~168 m is a reasonable verbal answer, not a fix. The residual puzzle is only that those frames sit 110–160 m north of the outline's north shore while showing birds at 13 m. Low priority. |
| Which named bridge is Crossing A? | **The one question that unlocks the rest.** Geno stood on its deck 15:08–15:10 on 2026-09-20. Nearest crossing by longitude is Mattison Avenue (85 m). Naming it places B and C by relative position. |
| Is Crossing C a crossing at all? | Probably not — it sits 25 m from the Railroad Ave head and the description (elevated view west down a narrower wooded channel, parking both banks) reads as the lake's western end. If so, segment S4 ("Crossing C → west end") collapses and the scheme needs renumbering. |
| What is in the eastern 365 m? | Never photographed. Two of the three crossings are in it. |
| ~~Does the lake continue west of Railroad Avenue?~~ | **SETTLED 2026-09-21.** A dedicated west-end survey found a tiled **WESLEY LAKE** sign (IMG_3516) and the **physical terminus** — trash racks and a culvert (IMG_3519/3520) — at ≈−74.0128. The supplied head is short by ~260 m. Corrected length 1346 m (0.84 mi) matches Geno's own estimate. No longer an inference. |
| Are MAT-?a and MAT-?b separate mats, or MAT-02/03 at distance? | Unresolved, and **position can no longer help** — the mats drift. Only a durable structural mark can settle it, and neither has one. |
| Do the mats carry asset tags or numbers? | Partly answered. IMG_2187 (06-17) shows an artificial teal/turquoise element standing proud of MAT base — a tie, stake or tag. Not readable at that range. One close photo settles it. |
| Gulls in flight on 2026-09-20 — real, and how many? | Detector found them in ~7 frames, 3 at once in IMG_3482. Entry 4 records no in-flight birds at all and concluded activity was "overwhelmingly loafing". Claude's read, unconfirmed. |

## Known fragilities

- The Cowork shell's `$HOME` is session-scoped, so pip installs vanish between
  sessions. `run.py` re-bootstraps. See ENVIRONMENT in `CLAUDE.md`.
- That shell's `claude` binary accepts only `claude -p "<prompt>"` — no flags.
  The `claude_cli` provider degrades automatically.
- **`logs/narrative.md` duplication — resolved 2026-09-20.** PROTOCOL.md §7
  already answered it: the folder is the system of record, and "memory is not a
  second copy of the log". Applied. Two further facts found while checking:
  (a) **Claude Code's memory for this project is empty** — the duplicate is in
  the *claude.ai* project memory, a different surface, editable only there;
  (b) the narrative entry is **not verbatim Geno** — it is third-person and was
  written up by Claude, while the header claimed "Geno's own words". Header
  relabelled, entry untouched. **Action left for Geno: prune the claude.ai
  memory copy down to a pointer.**
- The record now starts **2025-06-10**. Still no May photos in either year, and
  a 7-month gap between 2025-10-20 and 2026-01-31.
- Four cameras now appear in the record: iPhone 17, iPhone SE (3rd gen),
  Pixel 9, and whatever took the EXIF-stripped Entry 1-3 photos. The optics
  reasoning in `framing.py` (5.96mm / 2.22mm, no telephoto) is iPhone 17 only.

## Decisions already made — don't relitigate without new information

- **Individual ID is tiered A–D and only Tier A is real.** Most species at this
  lake carry no individual-distinguishing information; higher resolution does not
  change that. Image embeddings and perceptual hashing match photographs, not
  individuals.
- **In-chat photo uploads are not the pipeline.** They arrive with all EXIF
  stripped. Originals come in as a Google Photos zip through this folder.
- **The folder is the system of record.** Memory holds a pointer, not a copy.
- **Geofence is a bounding box, never a point radius**, and it has already been
  widened once after March photos fell outside it.
- **Processing is local on the MacBook Air**; Claude does identification and
  judgment, not ingest. The model is swappable via config.
- **The core count is on-lake birds only** (PROTOCOL.md §5b), and census class is
  derived from stratum rather than judged. Waders standing in the water count;
  pedal boats do not, even though they float — the count is the lake's own
  surface. Noted birds still get a full record.
- **Each floating mat is tracked individually**, matched by appearance only.
  The mats **float and drift within their anchoring** (Geno, 2026-09-20), so
  position is never an identity. Mat identity is tiered like bird identity (§6):
  a durable structural mark matches across seasons, foliage and position are
  within-season cues, and `MAT-unassigned` is the honest default. The durable
  marks live on the **base** — a manufactured module with bevelled edges,
  corners and countable planting ports — so they need a waterline photograph,
  not a better lens from the bank. MAT-01 is matched across 09-08 and 09-20 by
  its log; the others simply have not been photographed close enough yet.
- **No local general-purpose VLM.** The Air cannot run one worth having, and a
  specialist classifier beats a mid-size VLM at species anyway.
