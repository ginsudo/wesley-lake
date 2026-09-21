"""The lake's surfaces: open water, and each floating island as its own place.

The registry lives in `geography.md`, not here. That file is the system of record
for geography (PROTOCOL.md section 7) and it is what Geno edits; a second copy in
code would drift from it. This module parses the markdown table under
"## Floating islands" -> "### Registry" and nothing more.

A mat row is any row whose first cell contains MAT-<something>. Rows whose ID is
wrapped in asterisks-italics (*MAT-?a*) are UNRESOLVED sightings -- possible
duplicates of a confirmed mat -- and are deliberately NOT offered as assignable
surfaces. You cannot log a bird onto a mat that might not exist.

The mats FLOAT and drift within their anchoring, and the planting is deciduous, so
identity is split into a durable mark (structural; survives winter and movement --
the mat equivalent of PROTOCOL.md section 6 Tier A) and seasonal or positional
cues (good within one season or one walk, worthless outside it). `has_durable_mark`
is False for most mats, and that is the honest state of the registry, not a gap in
the parser: a mat without one is a within-season identity only.

Nothing here derives a mat from GPS, and nothing should. A drifting mat has no
position to be identified by.

    python3 pipeline/surfaces.py        # print the registry as parsed
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEOGRAPHY = os.path.join(ROOT, 'geography.md')

OPEN_WATER = 'open_water'
UNASSIGNED_MAT = 'MAT-unassigned'
_ID = re.compile(r'MAT-[0-9A-Za-z?]+')


_DATE = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')


def _frames(cell):
    """Frame numbers out of an evidence cell. Dates are stripped first: a cell
    reads "IMG_1128, 1129 (2026-04-27)" and 2026 is a year, not a frame."""
    return re.findall(r'\b(?:IMG_)?(\d{4})\b', _DATE.sub('', cell))


# geography.md is hand-edited prose, so the "durable mark" cell is matched against
# a documented set of ways of saying "there isn't one yet" rather than a rigid
# convention. Anything else counts as a recorded mark. Extend this list, and the
# test for it, if a new phrasing shows up.
_NO_MARK = re.compile(r'^\s*(none|not yet|not photographed|no\b|unknown|tbd|n/?a|[-—–?])',
                      re.I)


def _has_mark(cell):
    """True only if the cell actually describes a durable structural mark."""
    cell = (cell or '').strip().strip('*').strip()
    return bool(cell) and not _NO_MARK.match(cell)


def _tables(text, heading='## Floating islands'):
    """Yield (header_cells, [row_cells]) for markdown tables under `heading`.

    Shared with water.py: geography.md is the system of record for PLACES, so
    the mat registry and the water-quality stations both live there and are
    parsed out rather than duplicated in code.
    """
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().startswith(heading))
    except StopIteration:
        return
    key = heading.lstrip('# ').strip()
    header, rows = None, []
    for l in lines[start:]:
        if l.startswith('## ') and key not in l:
            break
        if not l.strip().startswith('|'):
            if header and rows:
                yield header, rows
            header, rows = None, []
            continue
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if set(''.join(cells)) <= set('-: '):
            continue                                    # separator row
        if header is None:
            header = [c.lower() for c in cells]
        else:
            rows.append(cells)
    if header and rows:
        yield header, rows


def _pick(header, cells, *wanted):
    """Value of the first column whose header contains any of `wanted`."""
    for w in wanted:
        for i, h in enumerate(header):
            if w in h and i < len(cells):
                return cells[i]
    return ''


def registry(path=None):
    """-> list of dicts, in file order, one per mat row.

    Parsed by COLUMN HEADING, not position, so the table in geography.md can grow
    a column without breaking this. Keys: id, confirmed, status, durable_mark,
    has_durable_mark, cues, evidence, evidence_frames.
    """
    path = path or GEOGRAPHY
    with open(path) as f:
        text = f.read()
    out = []
    for header, rows in _tables(text):
        for c in rows:
            if not c or not _ID.search(c[0]):
                continue
            mid = _ID.search(c[0]).group(0)
            status = re.sub(r'[*_]', '', _pick(header, c, 'status')).strip()
            durable = re.sub(r'[*]', '', _pick(header, c, 'durable')).strip()
            evid = _pick(header, c, 'evidence')
            out.append({
                'id': mid,
                # bold ID + a Confirmed status == assignable; italic ID == unresolved
                'confirmed': status.lower().startswith('confirmed'),
                'status': status,
                'durable_mark': durable,
                # "None identified" / "--" both mean there is no Tier-A-equivalent mark
                'has_durable_mark': _has_mark(durable),
                'cues': re.sub(r'[*]', '', _pick(header, c, 'cue', 'seasonal', 'signature')).strip(),
                'evidence': evid,
                'evidence_frames': _frames(evid),
            })
    return out


def mat_ids(path=None, confirmed_only=True):
    """Mat IDs a bird may be logged onto. Unresolved sightings are excluded --
    they may be duplicates of a confirmed mat, and logging onto one would invent
    a place. UNASSIGNED_MAT is always allowed: 'a mat, but I cannot say which'
    is an honest record; 'MAT-?b' is not."""
    ids = [m['id'] for m in registry(path) if m['confirmed'] or not confirmed_only]
    return ids + [UNASSIGNED_MAT]


def assignable(path=None):
    return [OPEN_WATER] + mat_ids(path)


def by_frame(path=None, date=None):
    """frame number (e.g. '3461') -> [mat ids], from the evidence column.

    Evidence of what has been PHOTOGRAPHED, not an assignment of any bird to a
    mat -- that stays a pass-2 judgement, because a frame can show two mats and
    a box carries no depth.

    Pass `date` to restrict to rows whose evidence names that date. A bare frame
    number is NOT unique across the archive -- iPhone numbering wraps, and a
    replaced phone restarts it -- so without a date this can attach the wrong
    mat to a same-numbered frame on another day. Callers that know the date
    should always pass it.
    """
    out = {}
    for m in registry(path):
        if date and date not in (m['evidence'] or '') and _DATE.search(m['evidence'] or ''):
            continue          # row is dated, and not for this date
        for fr in m['evidence_frames']:
            out.setdefault(fr, []).append(m['id'])
    return out


def describe(path=None):
    lines = []
    for m in registry(path):
        mark = 'confirmed ' if m['confirmed'] else 'UNRESOLVED'
        dur = 'durable mark' if m['has_durable_mark'] else 'NO durable mark'
        lines.append(f"{m['id']:<10} {mark} {dur:<16} {m['status']}")
        lines.append(f"{'':<10} {'':<11} {(m['durable_mark'] or m['cues'])[:78]}")
        if m['evidence_frames']:
            lines.append(f"{'':<10} {'':<11} frames: {', '.join(m['evidence_frames'])}")
    return '\n'.join(lines)


if __name__ == '__main__':
    print(describe())
    print()
    print('assignable surfaces:', ', '.join(assignable()))
