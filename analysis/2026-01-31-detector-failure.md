# Detector precision collapses on snow and ice — 2026-01-31

**Do not read a bird count off `analysis/2026-01-31-candidates.json`.**

## What happened

The 2026-01-31 sweep returned **323 detections, 179 of them at score ≥0.30** across
14 photos — by far the highest density in the archive (23 per photo against a
median of about 3). It looked at first like the largest bird concentration ever
recorded on the lake, a flock standing out on the ice.

It is snow.

A random sample of 30 detections at ≥0.30, read as native-resolution crops, is
essentially all irregular white lumps of drifted snow and broken ice. At most one
or two are ambiguous; none is a confident bird. Precision on this date is
somewhere around **0–7%**, against roughly **80–85% above 0.50 on summer water**.

## Why

A COCO-trained detector has a strong prior for "small pale blob, darker
surround" — which on liquid water is usually a gull, and on a frozen lake is
usually a lump of snow. The failure is not marginal, low-confidence noise either:
snow lumps scored up to **0.78**, well inside the band that is reliable in summer.
Confidence carries no warning here.

## What this costs

Recall was measured on three dates (2026-09-20, 2026-07-09, 2026-09-17) and found
no misses. **Every one of those was a liquid-water scene.** That measurement does
not generalise to winter, and the confidence it justified does not either.

Had this date been written into an append-only log off detector output, it would
have inserted roughly 179 phantom birds into the record — on the one date the
honest entry is "the lake was frozen and empty."

## What to do instead

- **Winter dates must be counted by eye.** The sweep is still useful as a place
  to look; its output is not a count.
- Raising the threshold does not fix it — the false positives reach 0.78.
- A real fix would need either a snow/ice-aware filter or a classifier stage on
  each box. Neither is worth building for one date a year; reading the frames is
  cheaper.
- `review.py`'s counting view is the right tool: the boxed frame makes the
  snow-lump pattern obvious at a glance, where the crop grid makes it obvious
  individually.

## The wider lesson

Detector quality was measured on the conditions the archive happened to contain
most of. Ice is a different regime, and there will be others — fog, glare off
wet mudflats, heavy algal bloom. Before trusting a sweep on a NEW kind of scene,
sample its crops.
