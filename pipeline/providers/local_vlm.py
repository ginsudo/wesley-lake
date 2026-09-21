"""Local vision model via an Ollama-compatible HTTP endpoint. NOT the default.

A MacBook Air cannot run a model large enough to compete with a frontier model on
age class, behaviour and hard marks. Kept so the choice stays open on other
hardware, and so the swap is a config edit rather than a rewrite."""
import base64, json, urllib.request, sys
sys.path.insert(0, __file__.rsplit('/', 2)[0])
import schema
from .claude_cli import extract_json
from .base import Identifier
class LocalVLM(Identifier):
    name = 'local_vlm'
    def __init__(self, endpoint='http://localhost:11434/api/generate',
                 model='qwen2.5vl:7b', timeout=300):
        self.endpoint, self.model, self.timeout = endpoint, model, timeout
    def identify(self, crop_path, context=''):
        img = base64.b64encode(open(crop_path, 'rb').read()).decode()
        body = json.dumps({'model': self.model, 'stream': False,
                           'prompt': schema.build_prompt(crop_path, context),
                           'images': [img]}).encode()
        req = urllib.request.Request(self.endpoint, body,
                                     {'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                out = json.loads(r.read()).get('response', '')
        except Exception as e:
            return [schema.blank(crop_path, notes=f'provider error: {e}',
                                 provider=self.name)]
        recs = extract_json(out) or []
        clean = []
        for r in recs:
            rec = schema.blank(crop_path, provider=self.name, model=self.model)
            rec.update({k: v for k, v in r.items() if k in rec})
            clean.append(rec)
        return clean or [schema.blank(crop_path, provider=self.name,
                                      notes='unparseable provider output')]
