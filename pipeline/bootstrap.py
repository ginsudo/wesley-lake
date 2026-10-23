"""Dependency bootstrap that works in BOTH environments (see ENVIRONMENT in
../CLAUDE.md) without the caller caring which one it is in.

1. Cowork Linux VM: $HOME is session-scoped, plain `pip install` works, and
   anything installed vanishes next session. Install and carry on.
2. Native macOS: `python3` is Homebrew's, which is PEP 668 "externally
   managed" — `pip install` is REFUSED, including `--user`. A virtualenv is
   the only supported route.

So: try a direct install; if that is refused, build a venv, install there, and
re-exec the calling script with the venv's interpreter. Costs one re-exec, once.

If the running Python cannot install them at all (Dodo's python3 is 3.15 and
onnxruntime has no 3.15 wheel, WL-03/04), try FALLBACK_PYTHONS in order and
use the first that can, printing one line naming it. If none can, fail and
list what was tried.

The venv lives OUTSIDE the project, keyed by platform and Python version:
    ~/.cache/wesley-lake/venv-<platform>-<machine>-<pyX.Y>
Outside because CLAUDE.md is emphatic about stray files in the project; keyed
because the same project folder is reachable from macOS/arm64 AND from the
Linux/aarch64 VM, and one venv cannot serve both.
"""
import os, sys, subprocess, importlib

GUARD = 'WESLEY_BOOTSTRAPPED'

# Interpreters tried, in this order, when the running Python cannot install the
# deps (WL-03/04: onnxruntime has no 3.15 wheel and Dodo's python3 is 3.15).
# The running Python is always tried first. This is the ONE place to change.
FALLBACK_PYTHONS = ('3.14', '3.13')
# Searched after $PATH. Homebrew's versioned pythons live here on Apple silicon.
EXTRA_DIRS = ('/opt/homebrew/bin',)
# Versions already found unable to install, carried across re-execs.
TRIED = 'WESLEY_PY_TRIED'

# The detector's deps, in one place so run.py can settle the interpreter up
# front (before ingest) instead of re-exec'ing mid-run from detect.py.
DETECTOR_DEPS = (['PIL', 'pillow_heif', 'numpy', 'onnxruntime'],
                 ['pillow', 'pillow-heif', 'numpy', 'onnxruntime'])

def _cache_root():
    base = os.environ.get('XDG_CACHE_HOME') or os.path.expanduser('~/.cache')
    return os.path.join(base, 'wesley-lake')

def _ver():
    return f'{sys.version_info.major}.{sys.version_info.minor}'

def venv_dir(ver=None):
    tag = f'{sys.platform}-{os.uname().machine}-py{ver or _ver()}'
    return os.path.join(_cache_root(), f'venv-{tag}')

def _venv_python(d):
    for rel in ('bin/python', 'Scripts/python.exe'):
        p = os.path.join(d, rel)
        if os.path.exists(p): return p
    return None

def _missing(mods):
    out = []
    for m in mods:
        try: importlib.import_module(m)
        except ImportError: out.append(m)
    return out

def _pip(py, pkgs):
    r = subprocess.run([py, '-m', 'pip', 'install', '--quiet',
                        '--disable-pip-version-check', *pkgs],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or '') + (r.stdout or '')

def find_python(ver, path=None, extra=EXTRA_DIRS):
    """Path of an executable `python<ver>` on PATH or in `extra`, else None."""
    dirs = (os.environ.get('PATH', '') if path is None else path).split(os.pathsep)
    for d in [*dirs, *extra]:
        p = os.path.join(d, f'python{ver}')
        if d and os.path.isfile(p) and os.access(p, os.X_OK): return p
    return None

def candidates(path=None, extra=EXTRA_DIRS):
    """[(version, interpreter-or-None)]: the running Python, then FALLBACK_PYTHONS."""
    cur = _ver()
    out = [(cur, sys.executable)]
    out += [(v, find_python(v, path, extra)) for v in FALLBACK_PYTHONS if v != cur]
    return out

def select(cands, attempt, skip=()):
    """First candidate `attempt(ver, py)` can make work.

    attempt returns (venv_python or None, log). Returns (ver, py, venv_python,
    failed_versions). Raises RuntimeError naming every candidate tried, and how
    it failed, if none works. No silent fallback.
    """
    tried, failed = [], []
    for ver, py in cands:
        if ver in skip:
            tried.append(f'python{ver}: already failed'); continue
        if not py:
            tried.append(f'python{ver}: not found on PATH or in {", ".join(EXTRA_DIRS)}'); continue
        vpy, log = attempt(ver, py)
        if vpy: return ver, py, vpy, failed
        failed.append(ver)
        last = [l for l in (log or '').strip().splitlines() if l.strip()]
        tried.append(f'python{ver} ({py}): {last[-1] if last else "failed"}')
    raise RuntimeError('no Python could install the dependencies. Tried:\n  '
                       + '\n  '.join(tried))

def _attempt(ver, py, modules, packages):
    """Make venv-<ver> hold `modules`; return (its python or None, log)."""
    d = venv_dir(ver)
    vpy = _venv_python(d)
    if not vpy:
        print(f'creating venv {d} (one time; Homebrew python refuses direct installs)',
              file=sys.stderr)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        r = subprocess.run([py, '-m', 'venv', d], capture_output=True, text=True)
        vpy = _venv_python(d)
        if r.returncode != 0 or not vpy:
            return None, f'venv creation failed: {r.stderr or r.stdout}'
    if not _missing_in(vpy, modules):
        return vpy, ''
    print(f'installing {" ".join(packages)} into {d} ...', file=sys.stderr)
    ok, log = _pip(vpy, packages)
    if ok and not _missing_in(vpy, modules):
        return vpy, ''
    return None, log or 'installed, but modules still not importable'

def ensure(modules, packages=None):
    """Make `modules` importable, by whatever route this platform allows.

    modules  -- import names to check, e.g. ['PIL', 'pillow_heif']
    packages -- pip names to install; defaults to `modules`

    Returns normally once the modules are importable. May re-exec the process
    into a venv -- built from the running Python, or failing that from the
    first of FALLBACK_PYTHONS that can install them (this call then never
    returns). Raises RuntimeError, listing what was tried, if none can.
    """
    packages = packages or modules
    if not _missing(modules): return

    ok, log = _pip(sys.executable, packages)
    if ok and not _missing(modules): return

    skip = {v for v in os.environ.get(TRIED, '').split(',') if v}
    if sys.prefix != sys.base_prefix:
        skip.add(_ver())          # the direct install above WAS this venv's try
    ver, base, vpy, failed = select(
        candidates(), lambda v, p: _attempt(v, p, modules, packages), skip)
    print(f'bootstrap: using Python {ver} ({base}) via {os.path.dirname(os.path.dirname(vpy))}',
          file=sys.stderr)
    env = dict(os.environ, **{GUARD: '1', TRIED: ','.join(sorted(skip | set(failed)))})
    os.execve(vpy, [vpy, *sys.argv], env)   # does not return

def _missing_in(py, modules):
    probe = ('import importlib,sys\n'
             'ms=%r\n'
             'bad=[]\n'
             'for m in ms:\n'
             '    try: importlib.import_module(m)\n'
             '    except ImportError: bad.append(m)\n'
             'sys.exit(1 if bad else 0)\n') % (list(modules),)
    return subprocess.run([py, '-c', probe], capture_output=True).returncode != 0
