# Wesley Lake bird board — design plan

Written 2026-10-22 by Claude (Cowork), at Geno's request. Status: **plan, not
built.** Read with `STATE.md`, `PROTOCOL.md` §5b/§6/§8/§9 and `geography.md`.

---

## 1. What the board is for

### Stated goals (Geno's, in the Project instructions, PROTOCOL §0 and memory)

1. **The cygnets.** The 2026 brood is "what he most wants tracked." The
   cormorants second.
2. **Birdwatching is a pleasure as well as data.** "The record should be
   rigorous, the tone should not be grim."
3. **Water quality and habitat**, with birds as one thread of a lake-health
   project, plus civic routes (Wesley Lake Commission, Monmouth CLONet).
4. **Learning to tell species apart** (narrative, 2026-09-15).
5. **The folder is the system of record.** Nothing durable lives only in a chat
   or a second copy; "two copies drift."

### Revealed goals (what the project's own files show he cares about)

6. **Honesty about uncertainty is the project's backbone.** Tiers A–D, ranges
   not midpoints, lower bounds, "sightings not individuals," `not_assessable` ≠
   zero, CONFIRMED vs Claude's read, effort bias. A naive chart would undo all
   of it. **The visual grammar has to carry these rules, not a footnote.**
7. **Geography is how he thinks about the lake.** Segments, crossings, the WQ-1
   rack, and mats as places with their own IDs.
8. **The record is shaped by its gaps, and he plans walks around them.** STATE's
   pending list is mostly field work: a winter walk, the eastern third, a fixed
   transect, WQ-1 on every west-end visit. So the board should be a
   **where-to-walk-next** tool as much as a scoreboard.
9. **Hand-maintained rollups go stale.** `2026-season-rollup.md` and
   `patterns.md` both did, and patterns.md says outright: "write the generator
   or drop the label." **Nothing on the board may be hand-typed.**
10. **He reads things on his phone,** away from the Air.

### So the board's job, in one line

> A phone-first page, regenerated from `analysis/records/`, that shows how the
> swan family and the lake are doing, makes the record's limits visible at a
> glance, and points at the next walk.

### Non-goals

- Not a place to *make* judgements. Confirmations, IDs and corrections stay in
  records/logs in git; the board only displays them.
- Not an abundance index. Effort is too uneven (STATE, pending item 3) until a
  fixed transect exists.
- Not a photo gallery (photos are optional, phase 4).

---

## 2. Visual grammar: the honesty rules, made visible

These hold for every panel. They are the acceptance test for the design.

| Rule (source) | How it shows |
|---|---|
| Counts are ranges (§9) | `count_range` drawn as a min–max bar or "4–6"; never a midpoint, never rounded up |
| Counts are lower bounds | "≥" convention in the legend; partial-view counts drawn hollow |
| Sightings, not individuals (§8) | No "total birds" anywhere. Season sums are labelled **bird-sightings** |
| Core vs noted (§5b) | Two series, never stacked into one. Noted birds get their own panel |
| Claude's read vs CONFIRMED (§9) | Confirmed = solid mark + ✓; Claude's read = outline. Uses the `confirmation` field |
| Tiers (§6) | Only Tier B (the pair) and Tier C (the brood) get identity tracks. Tier D species show counts only |
| Not assessable ≠ zero (§3a) | Hatched grey cell, never a 0 or a blank |
| No data ≠ no birds | S1 is "never photographed," hatched, not an empty bar |
| Effort beside every count | Each date shows photos/stops next to its birds, so a low count reads against a short visit |
| Small n | Every aggregate shows its n. No trend line below n=4 (§3a's "means something by the fourth") |
| Mats have no position (§5b, geography) | **Mats are never drawn on the map.** They are a list/table |
| Time (Gene's time rules) | Dates in ET. "Days since last walk" is computed when the page is viewed, not baked in |

---

## 3. Information architecture (phone-first, one scroll, top to bottom)

**0. Header.** Last walk (date, plus days since, computed on view), span of the
record, number of dates, and one always-visible line: *"Counts are lower bounds
and sightings, not individuals. IDs are Claude's read unless ✓."*

**1. The swan family** (first, because it's what he most wants).
- A timeline from the nest (MAT-04, 2026-04-27) to today: adults present
  (0/1/2) and cygnets seen per date, full counts solid and partial views hollow.
- Growth and molt notes as captions taken from the records (downy → contour
  feathers → brown-grey → "still no white").
- Status line, generated: last full count, last date any swan was seen, and how
  many walks since then had none, **with those walks' segments and effort**,
  so absence reads as absence-from-view. (Cygnets of this species typically
  disperse or get driven off in their first autumn or winter. That's general
  knowledge, not from a source here, so it stays off the board until a record
  supports it.)
- Data: `logs/individuals.md` SWAN-B01/B02 and SWAN-C01, cross-checked against
  records with `individual_id` / `tier` B or C.

**2. Last walk card.** Segments walked, core and noted birds by species, water
record if any, and a link to its bird-log Entry.

**3. The lake strip.** A schematic E→W strip (Ocean Ave → the trash racks), not
a map with coordinates:
- S1–S5 as bands, from `pipeline/lake.py:SEGMENTS`, with the three crossings
  and WQ-1 marked.
- Each band shaded by **effort** (visits, photos) with core sightings on top.
  S1 is hatched as never photographed.
- Tap a segment to see its species by stratum (§8 segment use).

**4. Season timeline.** A dot plot: dates across, species down. Dot area is the
max-simultaneous core count, a range bar where min≠max, and hollow for Claude's
read. An **effort track** runs underneath (photos and stops per date), and the
winter hole is visible as empty months.

**5. Species list.** For each species: first seen, last seen, number of dates,
max count, tier, and confirmation status, with a "first for the log" marker.
Then a second, deliberately playful list: **"Wanted this winter"**, the coastal
lagoon winter species from PROTOCOL §0 (Brant, Bufflehead, scaup, Ruddy Duck,
Red-breasted Merganser, American Coot, Great Cormorant). Each one ticks over
when a record first contains it. This serves the learning goal and the gap
goal at once.

**6. Floating mats.** A table per mat ID: identity status (durable mark /
within-season / unresolved), dates seen, how often occupied and how often empty,
species, and max at once. `open_water` gets a row as its own surface (§8).
Nests are flagged. Data: the `surface` field plus the `geography.md` registry
via `pipeline/surfaces.py`.

**7. Water.**
- WQ-1: one card per visit with the categorical fields, `not_assessable`
  hatched, and the litter range. A banner reads "baseline, not a trend" until
  n≥4.
- The archive-wide notable events (Entry 9: brown water dates, the drum, the
  carcass, the green patches) as a dated list.
- Water-health crossover (§8: cormorants/herons as a fish proxy, geese/gulls as
  a nutrient proxy) **only as labelled hypotheses**, phase 3, and only once
  there's enough to show.

**8. Gaps and next walk.** Generated, not hand-written:
- A coverage calendar (month × walks) that shows the Nov–Feb hole.
- A segment coverage list (S1 never, S2 twice).
- WQ-1 visits so far against the four needed for a series.
- One-photo questions from the open-questions table that a walk could close
  (Crossing B, mat tags, MAT-?a/?b), pulled from a small machine-readable list
  so they don't go stale. See §5 below.

**9. Noted birds.** Flight, bank, perches and the feeder station, never folded
into core. Overflights are listed separately, as §8 asks.

**Footer: provenance.** Generated-at time (ET), the git commit of `records/` it
was built from, the number of record files read, any `validation_problems`, and
the schema version. Every number on the page should trace back to a record
file.

---

## 4. Architecture

```
analysis/records/*.json ─┐
geography.md (mats) ─────┤
pipeline/lake.py ────────┼─► pipeline/board.py ─► board/board-data.json  (git-ignored, regenerable)
logs/individuals.md ─────┤                     └─► board/rollup.md        (replaces the hand tables)
logs/bird-log.md (index)─┘
                                   board-data.json ─► published page (claude.ai)
```

- **`pipeline/board.py`** is pure and deterministic. It reads only repo files
  (no photos), so it can run on the Air without touching the Dodo share. It
  emits one schema-versioned `board-data.json`. Every derived number keeps its
  `n` and the record files it came from.
- **`run.py` calls it last**, so "go check for new photos" refreshes the data
  with no extra step. It also runs standalone.
- **The same generator writes `board/rollup.md`**: the per-date, by-month,
  species, segment and surface tables. This finally answers patterns.md's
  "write the generator or drop the label." The old `2026-season-rollup.md`
  stays in records/ (never delete) with a "superseded by board/rollup.md" note.
  The prose judgements in patterns.md stay hand-written there.
- **Publishing:** the page is a claude.ai artifact that only ever renders
  `board-data.json`. It's never hand-edited. Republishing joins the PROTOCOL §4
  close-out ("after logging, regenerate and republish the board"), and its URL
  goes in STATE.md.
- **Two forms, one data file.** The published page is for the phone. The same
  file can drive a local `board/index.html` for when claude.ai isn't wanted
  (phase 4, optional).

### Page technology: decide in phase 0

The account has a **Dashboard** artifact type ("every number shows where it came
from", which fits rule 6). Unknown until tried: whether it can draw the custom
pieces (the lake strip, the hollow/solid range marks, the brood timeline). The
fallback is a hand-built artifact page with inline SVG, which gives full control
but more code. Phase 0 settles this on real data; no hunch decides it.

---

## 5. Small schema additions (the only record changes)

- **`open-questions.json`** (repo root or `analysis/records/`): the
  "one photo settles it" questions from STATE, each with id, question, the
  segment where a photo would answer it, and status. STATE's table can stay as
  prose; this file is what the board reads. *(Geno's call. Without it, panel 8
  drops the questions, because hand-typed board content is ruled out.)*
- **Optional `board_frame`** on a record: the one native-resolution crop to show
  for that sighting (phase 4 only).

No other record changes. Everything else the board needs is already in the
fields: `count_range`, `confirmation`, `tier`, `surface`, `segment`,
`census_class`, `age_class`, `source`.

---

## 6. Phases and acceptance

**Phase 0: spike (one short session).** Create a Dashboard artifact and
render panels 1 and 4 from a hand-run extract of the existing records. Pass
condition: it can draw a range mark, a hollow vs solid mark, and a horizontal
strip. Otherwise use a hand-built page. *Decision point for Geno.*

**Phase 1: generator.** `pipeline/board.py` plus `board-data.json` schema plus
`board/rollup.md`, wired into `run.py`. Load the testing-principles skill first.
Tests cover the honesty rules, not the plumbing: a Tier D record can never
produce an identity track, a range never collapses to a point, noted never adds
into core, `not_assessable` never becomes 0, n<4 suppresses a trend, S1 shows as
no-data. Acceptance: the rollup's numbers match Entry 5 and patterns.md where
those are known-good, and the differences are explained (patterns.md already
lists known staleness).

**Phase 2: board v1.** Header, swan family, last walk, season timeline,
species list with "Wanted this winter", gaps panel, footer. Published, with the
URL in STATE. Acceptance: readable at phone width, every number traceable to a
record, and Geno can answer "how are the cygnets?" in five seconds.

**Phase 3: geography and water.** Lake strip, mats table, water panel, noted
birds.

**Phase 4: optional.**
- Photos: one small crop per species or brood date, uploaded to the artifact.
  Photos then live on claude.ai (private until shared), a second place.
- Excerpts from `narrative.md`, **verbatim and marked "(Geno)" only**, never
  Claude's write-ups.
- A local HTML twin.
- A civic version for the Commission or CLONet (see §7).

---

## 7. Open decisions for Geno

1. **Who sees it.** Just Geno, or eventually the Commission or CLONet? A shared
   version shows walk dates and times, which is a pattern of when he's at the
   lake. The civic version would drop times and maybe dates.
2. **Dashboard type vs hand-built page**, after the phase 0 spike.
3. **Photos on the board** (phase 4), yes or no.
4. **`open-questions.json`**: worth the small file, or drop questions from the
   board?

## 8. Risks

- **The board outranks the log in people's heads.** That's why it's generated
  only, carries a provenance footer, and has no edit path.
- **The board goes stale like the rollups did.** Regeneration is in run.py and
  republishing is in the §4 checklist. The header's computed days-since makes
  staleness visible.
- **Charts flatter thin data.** Hence the n display, the effort tracks, no
  trends below n=4, and the always-visible caveat line.
- **The Dashboard type can't draw the strip.** That's phase 0's job to find out.

---

## 9. Phase 0 result (2026-10-22)

**Built:** a private Dashboard artifact, "Wesley Lake bird board (phase 0
test)", https://claude.ai/artifact/LQ9X9cyWsqXANuHMbt9NkL. Panels: the takeaway
line, the swan family, the season dot plot with effort track, and the lake
strip. Data is a one-off extract (`work/_board-p0/*.json`, disposable), not
`board.py`.

**On paper, the type passes.** Its instructions allow any d3 drawing the page's
code can do, including custom charts drawn by hand. All three pieces are custom
SVG: range bars, hollow/solid marks and the strip. Every chart is tied to a
named dataset, so each number shows its source. The type's automatic page check
started and then left no result, so **the page has not been seen working.**
Geno looking at it at phone width is the actual pass/fail.

**Constraints the type imposes**, which phase 1 should design for:
- No numbers in markup. Every figure comes from a dataset or a `dash.calc`.
  This matches the "nothing hand-typed" rule.
- Data goes in as uploaded files (≤8 MB each). Refreshing means a new upload
  plus updating the dataset document. That's a Claude step, so it belongs in
  the §4 close-out, not in `run.py`.
- The page is private until shared from its Share menu, and attached files can
  be read by anyone who can open it.

**Found in the data, for phase 1:**
- `confirmation` is free text (e.g. "Canada Goose as a regular species —
  CONFIRMED"), not a status field. The extract treats "contains CONFIRMED" as
  confirmed. The schema wants a real enum.
- `pipeline/lake.py` still bounds S5 at −74.02000 ("extent unresolved").
  geography.md settled the terminus at −74.01283 on 09-21. The extract used
  geography.md.
- The effort for 2026-10-22 is a lower bound: its candidates file is in Dodo's
  data root, not the Air's `analysis/derived/`. `board.py` needs effort from
  the data root or from the record itself.
- The 2026-09-17 geese show as 22–26 (an additive record), where the old
  rollup showed 10 (max at once). The board marks additive counts with a
  square. Phase 1 should decide whether additive records go into the core
  series at all.
- Swan "walks since last seen" is computed across all segments. A walk that
  never reached the swans' usual stretch still counts as "none in view".
