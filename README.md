# Wesley Lake

Bird observation and water-quality records for **Wesley Lake**, the boundary
water between Asbury Park and Ocean Grove, Monmouth County, New Jersey. A
coastal lagoon, roughly 1.3 km long, impounded behind the barrier beach and
draining to the ocean through a flume at Ocean Avenue.

31 dates, June 2025 – September 2026. 262 photographs, 82 records.

## What is here

| | |
|---|---|
| [`PROTOCOL.md`](PROTOCOL.md) | **the method** — what is recorded, how, and what is deliberately not |
| [`geography.md`](geography.md) | the lake's outline, its three crossings, the floating mats, the water station |
| [`STATE.md`](STATE.md) | where things stand, and every open question |
| [`logs/`](logs/) | the durable record — sightings, individuals, patterns, journal |
| [`pipeline/`](pipeline/) | local processing. One command: `python3 pipeline/run.py` |
| [`analysis/records/`](analysis/records/) | per-date observation and water records |

## The idea

Photographs are swept by a small local detector at native resolution, which
finds birds a person scanning contact sheets misses. Everything the machine can
do is deterministic and re-runnable. Everything that needs a judgement —
species, counts, what the water looks like — is made by a person looking at
native-resolution crops, and recorded against a schema that refuses to let a
guess pass as a fact.

The [pipeline README](pipeline/README.md) has the split in one table.

## Some things it has found

- The 2026 mute swan brood of four **survived the whole season**. Read September
  alone and it looks like 4 → 2; it was a partial view.
- A swan **nest on a floating treatment mat**, April 2026 — the mats are a
  nesting substrate, not just a roost.
- **Canada Goose is the lake's second species** (36 sightings). The log
  previously held one undated mention of geese.
- The lake **freezes** bank to bank.
- A **dumped drum**, a floating carcass, and litter collecting at the outflow
  trash racks — found by an exhaustive sweep after a sampled one wrongly
  concluded the lake photographed clean.

## What it will not tell you

A third of the lake — 363 m at the eastern end — has never been photographed.
Counts are maximum-simultaneous lower bounds, not censuses. Effort is uneven:
eleven of 31 dates are a single stop of 1–5 photographs. And **one** date falls
in November–February, so every species proportion here is a breeding-season
proportion of a lake whose winter birds are the interesting ones.

Each of those is stated in the record itself, not just here.

## Provenance

Species identifications are Claude's reading of the photographs unless a record
says `confirmed_by`. The raw photographs, the EXIF index and the detector output
are not in this repository — see [`.gitignore`](.gitignore) and
[`analysis/README.md`](analysis/README.md) for what is regenerable and what is
not.
