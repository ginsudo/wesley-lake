"""Provider interfaces. Every provider returns records matching schema.py.
The contract is the schema, not the model."""
class Identifier:
    name = 'base'
    def identify(self, crop_path, context=''):
        """-> list[dict] matching schema.blank()"""
        raise NotImplementedError
class Detector:
    name = 'base'
    def detect(self, image_path):
        """-> list[(x0,y0,x1,y1,score)] in fractional coords"""
        raise NotImplementedError
