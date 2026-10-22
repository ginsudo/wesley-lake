"""Where the bulky, regenerable data lives — separate from the repo.

ROOT is the repo: code, PROTOCOL, STATE, logs/, analysis/records/. Those never
move. DATA is the data root: photos/, archive/, staging/, work/ and
analysis/derived/ — big or regenerable, and Wesley Lake's permanent picture
archive lives on Dodo (Gene, 2026-10-22; MLJ-54).

Resolution, first hit wins:
    1. env WL_DATA
    2. config.json key "data_root" (relative paths resolve against ROOT)
    3. ROOT itself — so with neither set, behaviour is exactly as before.

Never point DATA at an SMB mount and run the pipeline from another machine:
the machine half runs on the machine whose disk holds DATA (PROTOCOL.md 1).
"""
import os, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def data_root():
    v = os.environ.get('WL_DATA')
    if not v:
        try:
            v = json.load(open(os.path.join(HERE, 'config.json'))).get('data_root')
        except (OSError, ValueError):
            v = None
    if not v:
        return ROOT
    v = os.path.expanduser(v)
    return os.path.abspath(v if os.path.isabs(v) else os.path.join(ROOT, v))


DATA = data_root()


def incoming_zips():
    """Zips waiting to be ingested: ROOT/*.zip and DATA/_incoming/*.zip."""
    found = glob.glob(os.path.join(ROOT, '*.zip')) + \
            glob.glob(os.path.join(DATA, '_incoming', '*.zip'))
    seen, out = set(), []
    for z in found:
        k = os.path.realpath(z)
        if k not in seen: seen.add(k); out.append(z)
    return sorted(out)
