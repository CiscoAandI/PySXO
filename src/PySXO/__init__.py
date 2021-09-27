from .workflows import Workflows
from .instances import Instances
from .core.decorators import cache
from .core.request_handler import RequestHandler

__version__ = '0.0.3'

class SXOClient(RequestHandler):
    @property
    @cache('_workflows')
    def workflows(self):
        return Workflows(self)
    
    @property
    @cache('_instances')
    def instances(self):
        return Instances(self)