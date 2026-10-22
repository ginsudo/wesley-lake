Superseded 2026-10-22 03:40 ET by MLJ claude/dodo-sides.md; not rolled out.
# To Master Learning Journal, from Wesley Lake: a Dodo mirror for every Project

Written 2026-10-22 07:10 UTC (03:10 ET), Cowork › Wesley Lake, on the Gair.

## Gene's request (his words, 2026-10-22)

> "ok what you just did, that's what I want for every project, so long as the
> Master Learning Journal sees fit to do so for the purposes of the project, and
> if there's any ambiguity, ask me."

Earlier in the same thread: "I would like to keep a durable set of essential
project files both here and on the Dodo in the Wesley Lake folder there. It's ok
for them to get 24 hours out of sync. I'll just ask in this project if I want a
refresh." He was also worried about "creating problems with source of truth or
speed of inference".

So MLJ decides, Project by Project, whether this pattern fits. Anything unclear
goes to Gene as a question.

## What "what you just did" was (the reference implementation)

1. **The Gair folder stays the single source of truth.** Here that is
   `~/Claude/Projects/Wesley Lake`, a git repo.
2. **A one-way copy to Dodo goes into the Project's own Studio folder.** Here that
   is `Claude Project Files/Wesley Lake`, reached on the Gair as
   `/Volumes/ginsudodojang/Claude Project Files/Wesley Lake`. It was empty before
   this. Copying runs Gair → Dodo only, and nobody edits the Dodo copy.
3. **Only the essential set is copied.** That means everything nothing else can
   regenerate, plus the code:
   - the root `*.md` files (STATE, PROTOCOL, CLAUDE, README, geography) and
     `.gitignore`
   - `logs/*.md`
   - `analysis/README.md` and `analysis/records/` (the hand-made judgements)
   - `pipeline/`, without `models/` (a 34 MB ONNX model) and without
     `__pycache__`

   Left out: photos, `work/`, `archive/`, `staging/`, `analysis/derived/` and
   `.git`.

   The result is 79 files, about 720 KB.
4. **The copy command** is `rsync -rt` with an include list, and no `--delete`.
   rsync writes each file under a temporary name and then renames it, so a file
   is never half-overwritten in place (rule R6). After copying, **every file is
   byte-compared** with `cmp`: 79 of 79 matched. An SMB copy that reports
   nothing can still have failed silently, so the comparison is what proves it
   worked.
5. **A `MIRROR.md` file on Dodo** says the copy is read-only, names the source,
   lists what was left out, and stamps the refresh time (ET) and the Gair's git
   HEAD, with a count of uncommitted changes.
6. **Refreshes happen only when Gene asks** in that Project. Up to about 24
   hours of staleness is accepted.
7. **No third copy in claude.ai Project docs.** It would add drift and not add
   access, since a Cowork session already reads the Gair folder directly.
8. **The decision is recorded** in the Project's STATE.md, under "Decisions
   already made". That edit is not yet committed to git: the Cowork shell can't
   commit there because deleting files is disabled, which leaves git lock files
   behind.

## Overlap MLJ should settle first: does `_air-mirror` already do this?

I read the desk while writing this. Item c-20261019-mlj-24 says "the Studio
mirror covers ~/Claude/Projects only". Items h-mlj-27 and c-20261021-mlj-02
mention a Studio `_air-mirror` and "air-mirror scripts" running as launchd jobs.
If that mirror already pulls the whole of `~/Claude/Projects` on a schedule, then
Wesley Lake now has **two** copies on Dodo:

- `_air-mirror`: automatic, complete, and presumably what backups rely on
- `Claude Project Files/Wesley Lake`: hand-curated, and refreshed only on
  request

I could not see `_air-mirror` from here (only the Wesley Lake folder on the share
is connected), so this is inferred from desk text, not checked. I'm about 80%
confident it covers Wesley Lake.

If it does, the part of Gene's ask that `_air-mirror` doesn't already meet is
narrower: **a small, curated working copy in each Project's own Studio folder,
which Dodo Claude sessions can read without digging through a full mirror**.
Whether that is worth a second copy is MLJ's call, and possibly Gene's.

## Questions for MLJ to decide, or to put to Gene

1. **Overlap.** Keep the curated per-Project copy, or rely on `_air-mirror`?
   This also covers whether to keep or retire the Wesley Lake copy just made.
2. **Projects whose source is already on the Studio** (LLM School, and Contacts
   Cleanup's Studio side). Skip them, or reverse the direction?
3. **Private-root Projects** (Ginsudo Law Office under `~/Documents/Claude`,
   which is not mirrored by design, plus Health Panel and Financial Planning).
   Should their essential sets go onto the Studio share at all?
   c-20261019-mlj-24 already has an open choice about backups for the private
   root.
4. **Refresh trigger.** On request only, as Gene said for Wesley Lake, or also
   at session end or on a schedule? A schedule would be a new launchd job on
   Dodo, so it needs Gene (rule R2 while he's away).
5. **Where the pattern lives.** A per-Project STATE or instructions line, a
   remote-work rule, or a small shared script (for example
   `tools/mirror-to-dodo.sh <project> <include-file>`) so the include lists stay
   consistent from Project to Project.

## Pointers

- Wesley Lake STATE.md, under "Decisions already made", in the bullet that
  starts "Dodo holds a one-way, read-only mirror"
- On Dodo: `Claude Project Files/Wesley Lake/MIRROR.md`
