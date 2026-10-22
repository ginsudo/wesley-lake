# Cross-species review — all nine species compared

Session write-up, 2026-10-22. Claude's work, from `logs/patterns.md` and
`logs/bird-log.md` Entries 1–9. No photographs were re-read; nothing here is a
new observation. PROTOCOL.md §7 (`analysis/` = per-session working analyses).

**What this adds:** the project had species composition (one column of totals)
but no cross-species comparison — surface use, date spread, age evidence and
breeding evidence side by side. That comparison is below, plus three findings
and a plain-prose account of the season for readers who are not going to open
the log.

---

## 1. Basis, and a staleness warning

The table is built on the **30-date rollup in `logs/patterns.md`**, which is
labelled `Generated 2026-09-20T19:10:17`.

**The record is now 31 dates.** Entry 8 (2026-09-21, the west-end survey) is in
the log and in `analysis/records/2026-09-21-observations.json` but is **not**
in the patterns tables. The delta is given in §3 rather than merged into the
table, because merging by hand would create a third set of totals that neither
`patterns.md` nor the records support. `patterns.md` is due its monthly rebuild;
after that, §3 should be deleted and the table regenerated.

Everything below is the **core count** (§5b, birds on the lake surface) unless a
cell says `noted`.

## 2. The comparison, at 30 dates

| Species | Core sightings (share) | Dates present | Peak | Where it sits | Age / breeding evidence |
|---|---|---|---|---|---|
| **Mute Swan** | 67 (47%) | 18 core + 1 bank-only | 6 (2 ad + 4 cyg) | Open water; nest on MAT-04; cygnets on a mat 08-15; adult on mown grass 06-19 | **Bred.** Nest 04-27, brood of 4 by 06-13, all 4 alive 09-19 |
| **Canada Goose** | 36 (25%) | 6 | 10 simultaneous; **~24–26 additive** (09-17, Entry 3/7) | Open water only | Adults + immatures (07-09, 09-17). No breeding evidence |
| **Mallard** | 17 (12%) | 9 core + 1 bank-only | 4–6 | **The only generalist** — open water, grass bank, and on a mat (06-17) | Both sexes; eclipse males. No breeding evidence |
| **Dbl-crested Cormorant** | 10 (7%) | 4 core + 1 dock | 5–6 | **Never on open water** — mats (MAT-01) and a dock | Juveniles + adults together (06-17, 09-08, 09-20) |
| **Large gull sp.** | 5 (3%) | 1 (09-20) | 5–6 | Open-water raft, east end; ~3 more in flight | Two age classes in one raft. Ring-billed vs Herring unresolved |
| **Great Blue Heron** | 1 (1%) | 1 (09-20) | 1 | Edge of MAT-03, stalking | Probably immature, ~65% — and Entry 6 shows that hedge is generous |
| **Duck sp. (mallard-type)** | 2 (1%) | 1 (09-20) | 2–3 | Open water, among the gulls | — |
| **Gull sp.** | 1 (1%) | 1 (09-19) | 1 | Open water, wing-drying | — |
| **(unidentified)** | 4 (3%) | 4 | 1 | Open water | Includes the **03-26 diving duck**, definitively not a mallard; a first if ever resolved |

### Contrasts

- **Swan dominance is an artifact of attention.** 47% is one resident pair and
  one brood, photographed repeatedly. By *dates present*, swan (19) and mallard
  (10) lead. By birds on the water at one moment, geese win.
- **Cormorants and swans divide the mats.** Cormorants are a structure bird —
  10 of 10 core sightings on a mat, plus one dock. Not once on open water.
  Swans use mats to nest and rest but live on the water.
- **Only mallards use all three strata** (open water, bank, mat). Geese use one.
- **Seasonality, thin but real.** Geese: Mar, Apr, Jul, Sep — absent from every
  June and August date. Cormorants: June, then September. Swans: every month
  photographed.
- **No Tier A bird in any species.** No band, tag, injury or odd feather in 219
  photographs (`logs/individuals.md`). Not a failure of looking — the hard-mark
  check has clean negatives on three dates.

### Not in the table

The white long-necked wader of 2026-09-17 (Great Egret or Snowy, a first either
way) — chat-only photos, EXIF stripped, Entry 7 judges it probably unresolvable.
And the Asbury-bank feeder station, never deliberately visited; those birds would
be almost entirely `noted`, not core.

## 3. Delta from Entry 8 (2026-09-21), not yet in patterns.md

| field | 30-date | + Entry 8 | 31-date |
|---|---|---|---|
| Mute Swan, core | 67 | +2–3 | **69–70** |
| (unidentified), core | 4 | +3–5 | **7–9** |
| Mallard, **noted** | 11 | +6 | **17** |
| Dates | 30 | +1 | **31** |

Two things in Entry 8 change the reading, not just the totals:

- **A full breeding-plumage drake mallard**, the first since March — every
  mallard from July onward reads "female or eclipse". The eclipse moult is
  finishing by late September. This is a phenology datum and the table has no
  column for it.
- **Adults present, no cygnets anywhere in 43 frames** — the first such date
  since June. Not evidence of loss (far west end, the family ranges the lake),
  but it is the first time the brood column could have been filled and wasn't.

Entry 9 (the water sweep) adds no bird records and does not affect the table.

## 4. Findings

### 4a. `patterns.md` miscounts the goose dates — fixed 2026-10-22

It read "36 sightings across **five** dates". The per-date entries give **six**:
03-26, 04-27, 07-09, 09-08, 09-10, 09-17. The 36 is right (it sums the low bound
of each range: 4+10+8+2+2+10). Corrected in place.

How it survived: the total was checked and the date count was not. A sentence
holding one verified number lends its credibility to the unverified one beside
it. Filed as a standards candidate.

### 4b. `patterns.md` is labelled generated and nothing generates it

Its header says `Generated 2026-09-20T19:10:17`. There is no generator —
`grep -rn "patterns" pipeline/` returns nothing. It is hand-maintained with a
machine label, which is why it could sit a month behind the log with no signal.
Either write the generator or drop the label and date it by hand.

### 4c. Two of the 31 dates may not be observation effort

The record opens 2025-06-10 and 2025-10-20 — both inside the geofence, both
birdless, 4 and 2 photos. But the watching began after the move to Asbury Park
in the following winter. If those are incidental visitor photographs rather than
birding, then "31 dates" overstates the effort denominator by two, and the two
blanks are not low-count birding days at all. Added to STATE.md open questions;
only Geno can settle it.

---

## 5. The season in prose

*(written by Claude, 2026-10-22 — not a narrative-journal entry. `logs/narrative.md`
is Geno's own journal and this does not belong in it. Kept here because it is the
most readable entry point to the season for someone who will not open the log —
the Commission, for instance.)*

The record begins with two failures to find anything. On the tenth of June, 2025,
at 17:58, four photographs near Pilgrim Pathway. On the twentieth of October, two
more from the same stretch, taken into the sunset, looking west. Six frames, no
birds. Then the file goes quiet for seven months.

It opens again on the thirty-first of January. The lake is frozen bank to bank,
snow on both shores, and the orange marker buoy is set in the ice where it
stopped. Fourteen photographs, and in them a man walking a frozen lake finds
nothing alive on it. Later a piece of software would go through those same frames
and announce a hundred and seventy-nine birds, every one of them a lump of
drifted snow, one of them with a confidence of 0.78.

The thaw comes in without ceremony. On the tenth of March there are mallards at
the far west end, some on the seawall and some dabbling below it. Then, on the
twenty-fifth, two adult mute swans in a single frame, together. Until that frame
there had only been *a swan*, which is an anecdote. Two swans in the same water,
and two again on the twenty-seventh, forty-eight hours later — that is a pair,
and a pair is a household. A dog came down the bank that afternoon and they did
not leave the water.

On the twenty-seventh of April, in two photographs and no more, there is a stick
nest built down into the bare woody stems of one of the floating mats the town
has anchored out there. One adult is sitting. The other stands beside it. Behind
them, out on the open water and entirely unnoticed at the time — noticed only
months later, by the detector, on frames human eyes had already gone over looking
for the nest — are ten or fifteen Canada geese, loafing.

The cygnets are on the water by the thirteenth of June. There are four, downy,
counted in one frame with one adult attending. They will be counted again and
again over the next fourteen weeks and the number will be four: four on the
sixteenth of June with the down giving way to feathers and both parents
bracketing them in line astern; four on the fifth of July; four on the eighth;
four on the eleventh of August and four on the twelfth, in what is still the
cleanest photograph in the archive — two adults, four cygnets, one mallard
alongside, nothing overlapping anything.

On the fifteenth of August all four are sitting on a floating mat, out of the
water, their bodies on the dark manufactured base of the thing, their reflections
under them. The adult floats behind. The mat beside that one is holding nothing
at all, which is also recorded, because an empty mat is a fact about a lake.

The mats turn out to be the lake's real furniture. The swans nested on one. The
cormorants roost on another, a particular one, identifiable across the whole
season by a dark log projecting from its base — the same timber on the eighth of
September, the nineteenth, and the twentieth. A juvenile cormorant stood on a mat
in June with a mallard, the only time a duck has been caught up on one rather
than swimming beside it, and that frame is also the one that gave away what the
mats are: a bevelled edge, a corner, planting ports, and some small teal
artificial thing standing proud of the base, a tie or a stake or a tag, not
readable at that distance.

September runs dense. On the fourteenth an adult swan goes fully over, head and
neck under, the only time anyone has photographed one of these birds actually
feeding. On the seventeenth a cormorant stands on bare dock planking at 10:05:04
with its feet entirely in focus and entirely unbanded — which sounds like nothing
and is the best piece of evidence in the archive, a clean negative rather than a
shrug. That same morning there are ten geese, counted exactly. That same morning,
too, a white long-necked bird sits in the trees at the water's edge, an egret of
one kind or the other, photographed through a chat window that stripped the file
of everything that would have let anyone find it again. It is probably lost for
good.

On the nineteenth all four cygnets are at the west-end bulkhead being hand-fed,
still brown-grey, no white anywhere on them, fifteen weeks old.

And on the twentieth, under an overcast sky, on a twenty-minute walk from the old
Carousel westward, at the edge of a floating mat: a great blue heron, standing,
and then crouched forward with its head out, hunting. Probably a young one,
though the case is thinner than it first looked — an adult has shed its plumes by
late September too, so the only real evidence is the tone of the bill.

Five days before that, the journal had it that he knew there were blue herons on
this lake and wasn't sure he'd ever seen one.

The day after, a west-end survey found six mallards asleep on a dock, one of them
a drake come back into full colour, and two swans mid-channel with no young
anywhere in forty-three frames.
