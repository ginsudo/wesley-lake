"""Identify via the Claude Code CLI, running headless.

Chosen as the default because it runs under the logged-in Claude subscription
rather than metered API billing. VERIFY THIS before relying on it -- plan/CLI
billing behaviour changes, and `claude --help` is the source of truth for flags.
"""
import json, re, subprocess, sys
sys.path.insert(0, __file__.rsplit('/', 2)[0])
import schema
from .base import Identifier

def extract_json(text):
    m = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.S)
    if m: text = m.group(1)
    else:
        i, j = text.find('['), text.rfind(']')
        if i < 0 or j < i: return None
        text = text[i:j+1]
    try: return json.loads(text)
    except json.JSONDecodeError: return None

class ClaudeCLI(Identifier):
    name = 'claude_cli'
    def __init__(self, binary='claude', model=None, timeout=180, extra_args=None):
        self.binary, self.model, self.timeout = binary, model, timeout
        self.extra_args = extra_args or []
    def _run(self, args):
        try:
            r = subprocess.run([self.binary] + args, capture_output=True,
                               text=True, timeout=self.timeout)
            return r.stdout or ''
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return f'__ERR__{e}'

    def identify(self, crop_path, context=''):
        prompt = schema.build_prompt(crop_path, context)
        args = ['-p', prompt]
        if self.model: args += ['--model', self.model]
        args += self.extra_args
        out = self._run(args)
        # Some environments support only bare `claude -p "<prompt>"`. Degrade.
        if out.startswith('__ERR__') or 'only `claude -p' in out or not out.strip():
            out = self._run(['-p', prompt])
        if out.startswith('__ERR__'):
            return [schema.blank(crop_path, notes=f'provider error: {out[7:]}',
                                 provider=self.name)]
        recs = extract_json(out)
        if recs is None:
            return [schema.blank(crop_path, notes='unparseable provider output',
                                 provider=self.name)]
        clean = []
        for r in recs:
            rec = schema.blank(crop_path, provider=self.name,
                               model=self.model or 'default')
            rec.update({k: v for k, v in r.items() if k in rec})
            clean.append(rec)
        return clean
