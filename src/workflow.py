from .core.base import Base
from attrdict import AttrDict

class Workflow(Base):
    def __getattr__(self, key):
        if isinstance(self._json.get(key), dict):
            return AttrDict(self._json[key])
        return self._json.get(key)