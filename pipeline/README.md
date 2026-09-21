# Wesley Lake — local pipeline (MacBook Air)

## The one thing to understand first

The work splits in two, and almost every confusion comes from blurring them:

| | | |
|---|---|---|
| **MACHINE** | ingest · EXIF · geofence · stops · contact sheets · **detector sweep** · review sheets · **water sheets** | `run.py`, all of it. Deterministic, idempotent, re-run any time |
| **EYES** | species · counts · stratum · surface · every water judgement | `observe.py` and `water.py` turn a person's (or a Claude session's) decisions into validated records |

**`run.py` cannot identify a bird or assess a lake, and does not pretend to.**
It prepares the material and then prints exactly what is still waiting.

    python3 pipeline/run.py       # everything the machine can do, then a to-do list
    python3 pipeline/status.py    # just the to-do list

## Run it

    cd ~/Claude/Projects/"Wesley Lake"
    python3 pipeline/run.py

Drop a Google Photos zip in the project root first; with no zip it rebuilds
derived products from `photos/`. Idempotent — safe to re-run any time. Stages:

1. **ingest** — unzip, EXIF, geofence against the lake outline, file by date
2. **build** — stop clustering, contact sheets, `analysis/session-index.md`
3. **detect** — the bird sweep, if `config.json` sets a detector. `"none"` is a
   clean no-op
4. **water** — build `work/<date>/water.jpg`, every frame cropped to its water
   band (PROTOCOL §3a)
5. **status** — what still needs eyes

Deps: handled automatically. On native macOS `pip3 install` is **refused** —
Homebrew's python is PEP 668 "externally managed" — so `bootstrap.py` builds a
venv under `~/.cache/wesley-lake/` (keyed by platform and Python version,
because the same folder is reachable from both macOS and the Cowork Linux VM)
and re-execs into it once. In the Cowork VM the plain install still works and
the venv is never created.

## Then the half a machine cannot do

    python3 pipeline/review.py <date>   # counting view + ID view, per sighting event
    # ...look at them, then write records through observe.py

    open work/<date>/water.jpg          # every frame's water band on one sheet
    # ...look at it, then write a record through water.py

Both writers validate against PROTOCOL and refuse to coerce: a record that
fails is written **with its problems attached**, never dropped.

## Modules
- `bootstrap.py` — makes deps importable in both environments. See Deps above.
- `exif.py` — HEIC EXIF via pillow-heif. **Validated against exiftool**, exact match.
- `track.py` — stop clustering and cumulative distance. This is what proved the
  "three batches" of 2026-09-20 were a single 20-minute walk.
- `sheets.py` — pass-1 contact sheets (overview only, never identification).
- `crop.py` — pass-2 native-resolution crops. Resolution-on-subject formula in the
  docstring.
- `detect.py` — **optional** detection stage. No-op unless `config.json` sets
  `roles.detector`. Sweeps every frame, writes crops + PROTOCOL 5a sub-crops to
  `work/<date>/crops/`, overlays to `work/<date>/overlay/`, and one record per
  detection to `analysis/<date>-candidates.json`. Skips dates already swept, so
  `run.py` stays cheap and idempotent; `--force` re-sweeps.
- `providers/yolox.py` — the detector. YOLOX-S, ONNX Runtime, CoreML + CPU.
- `surfaces.py` — parses the floating-mat registry out of `geography.md`. That
  file is the system of record; this module never holds a second copy.
  `python3 pipeline/surfaces.py` prints what it sees.
- `water.py` — **water-quality observations** (PROTOCOL §3a). Categorical only:
  surface state, ice, organic debris load on the trash rack, water level against
  its posts, marginal vegetation, a count of discrete litter items. Deliberately
  measures **no colour, clarity or turbidity** — illumination dominates the
  pixels (the same patch reads RGB 185 in sun and 89 in shade) and depth is not
  visible in a photograph. It opens no image at all, and there is a test
  asserting that. `python3 pipeline/water.py`
- `census.py` — rolls records into the PROTOCOL 5b numbers: core count, noted,
  per-surface and per-segment totals, including mats that held nothing. Refuses
  to sum one species twice in one sighting event unless a record says
  `additive`. `python3 pipeline/census.py analysis/<date>-observations.json`
- `schema.py` — the observation record and its validator. Enforces PROTOCOL
  rather than trusting whoever filled it in: Tier D with an individual ID, Tier A
  without a mark, a census class that contradicts its stratum, a mat ID not in
  the registry, a count outside its own range, `max_simultaneous` with no frames.
- `framing.py` — **deciding when two frames show the same birds**, so a count is
  not inflated by re-photographing. Three mechanisms, none of them appearance-
  based (PROTOCOL §6 forbids that, and there is a test asserting this module
  never opens an image):
  1. *stale-fix detection* — a bad GPS fix is identified by its neighbours, and
     resolved iteratively so a bad fix does not condemn the innocent frame next
     to it;
  2. *zoom bursts* — a wide frame followed seconds later by a zoomed one is one
     subject re-framed. Classified `lens_change` / `real_crop` / `interpolated`;
  3. *sighting events* — adjacent stops within 380 s and 55 m. Those numbers are
     **fitted to Entry 4's own hand-grouping** and `self_check()` fails if they
     stop reproducing it.
  Its output is a *candidate* grouping for pass 2, never a merge. It is a
  geometric heuristic and does not outrank an eyewitness — see log Entry 7,
  where it was wrong about a goose count because the photographer had turned.
- `lake.py` — the lake's outline, distance-to-water, and the segment scheme.
  The geofence asks "how far is this photo from the water" instead of "is it in
  this box"; the old box had to be widened twice. Read `LATITUDE_CONFLICT`
  before trusting the coordinates.
- `observe.py` — **the pass-2 writer.** Turns a reading of the crops into a
  validated record, and *derives* everything machine-knowable rather than
  letting it be typed: stop, event, segment, census class, and frame-level
  provenance back to the detections. Metadata that is typed is metadata that is
  eventually wrong — a bulk backfill once set `event: 1` on nine records
  spanning five events. `python3 pipeline/observe.py --check [--write]`
- `review.py` — the two views pass 2 actually needs, per sighting event. A
  **counting view** (boxed frames, since crops destroy the spatial relationships
  counting depends on) and an **ID view** (native-resolution crops, biggest
  score first). Leads with the peak single-frame count, not the event total.
  `python3 pipeline/review.py <date>`
- **Two provenance guards** (PROTOCOL 3, 3b), both enforced in code because
  both were holes found by asking "what if the photos weren't mine?":
  - `run.py` files a GPS-less photo to `photos/_no-gps/`. Previously the date
    alone put it in the dated record, which silently asserts a location.
  - `schema.py` / `water.py` / `census.py` carry `source`: `own_walk` or
    `external`. An external record needs a `source_note`, may not claim
    `count_exact`, `count_basis: additive`, `water_level` or `litter_count`,
    and `census.py` routes it to `presence_only` — it never touches a total.
- `test_pipeline.py` — 139 checks over all of the above: that `"none"` is a real
  no-op, that records failing `schema.validate` are written with their problems
  attached rather than dropped, that framing reproduces Entry 4's grouping, that
  every archived photo passes the geofence, that count=0 is not counted as a
  bird, and that S1 has never been photographed (if that one ever fails, someone
  has walked the eastern third), and that an external record cannot enter the
  core count.
- `census.py --water` — the water rollup, including the brown-vs-wind
  cross-tabulation. Currently inconclusive, and says why.
- `status.py` — what is done and what is waiting, per date. The answer to
  "where was I?". `python3 pipeline/status.py --todo`
- `run.py` — the machine half, end to end, then the to-do list.

## The detector

    "roles": { "detector": "yolox" }        # one word; "none" turns it off

**Model: YOLOX-S**, COCO-pretrained, class 14 = `bird`. 34 MB ONNX in
`pipeline/models/` (kept in the project, not a cache dir: the Cowork VM's `$HOME`
is session-scoped, and "fully offline" should survive a cold cache). Apache-2.0
for code *and* weights. ONNX Runtime is 21 MB; venv total ~160 MB. No GPU, no
torch. CoreML execution provider is used when present (~1.6x faster than CPU on
the Air; boxes identical, scores agree to ±0.003).

Why not Ultralytics YOLOv8/YOLO11, which is better per megabyte: AGPL-3.0, and a
heavy pip package that phones home by default. YOLOX is the best Apache-2.0
option with official static-shape ONNX exports, which is what the CoreML
provider wants anyway.

**It sweeps tiles, not whole frames.** These are 24 MP photos; letterboxing one
into the model's 640 px input is an 8.9x downscale, so a 30 px bird at the far
bank lands at 3 px — under the model's finest stride. The stage runs a grid of
overlapping 1200 px native tiles plus one whole-frame pass, then merges with NMS
that also drops boxes mostly *contained* in a higher-scoring one (tile edges cut
birds in half, and half-boxes have low IoU with whole-boxes).

Measured on the 52 frames of 2026-09-20, the same run with tiling turned off
(`"tile": 0`):

| | tiled | whole-frame only |
|---|---|---|
| detections | 229 | 52 |
| frames with >=1 box | 51 / 52 | 17 / 52 |
| cormorant roost found in | 19 / 20 frames | 4 / 20 |
| heron found in | 10 / 10 frames | 4 / 10 |
| west-end bird | found | **missed entirely** |
| runtime | 62 s | 20 s |

That gap is the whole reason the stage exists.

**Threshold.** `conf` defaults to 0.15, chosen on cost asymmetry — a distant bird
the sweep misses is invisible forever, a false positive costs one glance at a
crop — **not** fitted to the answers in `logs/bird-log.md`. Precision is strongly
score-dependent (hand-scored samples of 24 crops each): ~80-85% real birds above
0.50, roughly a third to a half below 0.25. Raise `conf` for a cleaner working
set; lower it before ever concluding a frame is birdless.

**It assigns no census class.** PROTOCOL 5b's core count is birds on the lake
surface, which follows from stratum — and a box has no depth, so it cannot tell
open water from shallows from a mat. Every detector record is
`census_class: "undetermined"` and counts toward nothing. What the stage does
instead is lay out the worksheet: `surface_candidates` on each record lists the
mats `geography.md` already knows appear in that frame.

**What it does not do.** It does not identify anything. Every record comes out
`species ''`, `confidence 'unknown'`, `tier 'D'`, `marks_checked false`. A box is
a claim about where to look. PROTOCOL.md section 4 pass 2 still has to happen.

## What to build next, in order of value

1. **Bird detection.** A small detector (YOLO-class, a few tens of MB) sweeping
   every frame at full resolution and emitting boxes. Runs fine on Apple Silicon
   CPU/ANE. This is the single biggest quality win available: it sweeps
   systematically where a human or a model eyeballing contact sheets silently
   misses distant birds with no way to know how many were missed.
2. **Hard-mark pass.** On every confident detection, auto-crop legs, neck and bill
   at native resolution into `work/<date>/marks/`. PROTOCOL.md §5a. This is the
   only place individual identity is real, and it is pure cropping — no model.
3. **Species classification** on each box. A purpose-built bird classifier will
   likely beat a general vision model at this. Verify what is offline-capable
   before committing.
4. **Candidate log emitter** — structured rows with per-box confidence, so only
   uncertain calls and first-for-the-log species need review.

## Known limits

- **The detector is unusable on snow and ice.** On 2026-01-31 it returned 179
  detections at >=0.30 and essentially every one was a lump of snow, scoring up
  to 0.78 — raising the threshold does not help. Recall was measured on three
  dates and found no misses; all three were liquid water. Winter dates must be
  counted by eye. See `analysis/2026-01-31-detector-failure.md`.
- **Counts are lower bounds.** Maximum-simultaneous within an event, never
  summed across frames — a naive total inflates about 2.8x.
- **A third of the lake has never been photographed.** Segment S1 not once, S2
  twice and both birdless. Every proportion the pipeline produces is an S3-S5
  proportion.

## What NOT to build

A local general-purpose VLM. A MacBook Air cannot run one large enough to be
worth it, and even on bigger hardware a mid-size local VLM would be worse than a
specialist classifier at species and worse than a frontier model at judgment. The
Air's constraint pushes toward the right architecture rather than away from it:
small specialist models locally, frontier model only on flagged cases.
