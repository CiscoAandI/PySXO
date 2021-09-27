import requests
import time
from .instance import Instance
from .core.decorators import cache
from .core.base import Base

class Instances(Base):

    @cache('_all')
    def all(self, **kwargs):
        return [Instance(self, i) for i in self._sxo._post(url=f"/v1.1/instances", **kwargs)]