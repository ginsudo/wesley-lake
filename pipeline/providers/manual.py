"""No automated inference. Emits blank records for a human -- or a Claude session
looking at the images directly -- to fill in. This is what the Cowork workflow
does today, and it is the honest fallback when no provider is configured."""
import sys
sys.path.insert(0, __file__.rsplit('/', 2)[0])
import schema
from .base import Identifier
class Manual(Identifier):
    name = 'manual'
    def identify(self, crop_path, context=''):
        return [schema.blank(crop_path, provider=self.name,
                             notes='awaiting review — no automated identification')]
