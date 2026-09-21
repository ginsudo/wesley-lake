import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.join(os.path.dirname(HERE), 'config.json')

def config():
    with open(CFG) as f: return json.load(f)

def get(role):
    c = config()
    name = c['roles'][role]
    if name == 'none': return None
    if name == 'claude_cli':
        from .claude_cli import ClaudeCLI
        return ClaudeCLI(**c.get('providers', {}).get('claude_cli', {}))
    if name == 'claude_api':
        from .claude_api import ClaudeAPI
        return ClaudeAPI(**c.get('providers', {}).get('claude_api', {}))
    if name == 'local_vlm':
        from .local_vlm import LocalVLM
        return LocalVLM(**c.get('providers', {}).get('local_vlm', {}))
    if name == 'yolox':
        from .yolox import YOLOXDetector
        return YOLOXDetector(**c.get('providers', {}).get('yolox', {}))
    if name == 'manual':
        from .manual import Manual
        return Manual()
    raise ValueError(f'unknown provider {name!r} for role {role!r}')
