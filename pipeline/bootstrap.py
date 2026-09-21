"""Dependency bootstrap that works in BOTH environments (see ENVIRONMENT in
../CLAUDE.md) without the caller caring which one it is in.

1. Cowork Linux VM: $HOME is session-scoped, plain `pip install` works, and
   anything installed vanishes next session. Install and carry on.
2. Native macOS: `python3` is Homebrew's, which is PEP 668 "externally
   managed" — `pip install` is REFUSED, including `--user`. A virtualenv is
   the only supported route.

So: try a direct install; if that is refused, build a venv, install there, and
re-exec the calling script with the venv's interpreter. Costs one re-exec, once.

The venv lives OUTSIDE the project, keyed by platform and Python version:
    ~/.cache/wesley-lake/venv-<platform>-<machine>-<pyX.Y>
Outside because CLAUDE.md is emphatic about stray files in the project; keyed
because the same project folder is reachable from macOS/arm64 AND from the
Linux/aarch64 VM, and one venv cannot serve both.
"""
import os, sys, subprocess, importlib

GUARD = 'WESLEY_BOOTSTRAPPED'

def _cache_root():
    base = os.environ.get('XDG_CACHE_HOME') or os.path.expanduser('~/.cache')
    return os.path.join(base, 'wesley-lake')

def venv_dir():
    tag = f'{sys.platform}-{os.uname().machine}-py{sys.version_info.major}.{sys.version_info.minor}'
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

def ensure(modules, packages=None):
    """Make `modules` importable, by whatever route this platform allows.

    modules  -- import names to check, e.g. ['PIL', 'pillow_heif']
    packages -- pip names to install; defaults to `modules`

    Returns normally once the modules are importable. May re-exec the process
    (this call then never returns). Raises RuntimeError if it cannot succeed.
    """
    packages = packages or modules
    miss = _missing(modules)
    if not miss: return

    ok, log = _pip(sys.executable, packages)
    if ok and not _missing(modules): return

    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        raise RuntimeError(f'cannot install {packages} into the active venv:\n{log}')
    if os.environ.get(GUARD):
        raise RuntimeError(f'still missing {miss} after re-exec into a venv:\n{log}')

    d = venv_dir()
    py = _venv_python(d)
    if not py:
        print(f'creating venv {d} (one time; Homebrew python refuses direct installs)',
              file=sys.stderr)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        subprocess.run([sys.executable, '-m', 'venv', d], check=True)
        py = _venv_python(d)
    if not py:
        raise RuntimeError(f'venv created but no interpreter found under {d}')

    if _missing_in(py, modules):
        print(f'installing {" ".join(packages)} into {d} ...', file=sys.stderr)
        ok, log = _pip(py, packages)
        if not ok:
            raise RuntimeError(f'pip install {packages} failed in {d}:\n{log}')

    env = dict(os.environ, **{GUARD: '1'})
    os.execve(py, [py, *sys.argv], env)   # does not return

def _missing_in(py, modules):
    probe = ('import importlib,sys\n'
             'ms=%r\n'
             'bad=[]\n'
             'for m in ms:\n'
             '    try: importlib.import_module(m)\n'
             '    except ImportError: bad.append(m)\n'
             'sys.exit(1 if bad else 0)\n') % (list(modules),)
    return subprocess.run([py, '-c', probe], capture_output=True).returncode != 0
