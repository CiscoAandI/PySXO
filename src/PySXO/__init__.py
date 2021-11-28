import logging

LOGGER = logging.getLogger(__name__)

from .workflows import Workflows
from .instances.list import Instances
from .core.decorators import cache
from .core.request_handler import RequestHandler

__version__ = '0.0.15'


class SXOClient(RequestHandler):
    def __init__(self, client_id: str, client_password: str, cache: bool=False, dry_run: bool=False):
        """
        Main SXO Client object.

        Example::

            client = SXOClient(client_id='my_client_id', client_password='my_client_password')
            client.workflows

        :param client_id: The Client ID for the SXO API client.
        :param client_password: The Client password for the SXO API client.
        :param cache: Whether or not to perform client-side caching. Default: False
        :param dry_run: Whether or not to perform mutative changes. This is useful for debugging. Default: False
        """

        self.cache = cache
        self.dry_run = dry_run
        self.client_id = client_id
        self.client_password = client_password
        
        super().__init__(
            client_id=client_id,
            client_password=client_password,
            cache=cache,
            dry_run=dry_run
        )

    @property
    @cache('_workflows')
    def workflows(self):
        return Workflows(self)

    @property
    @cache('_instances')
    def instances(self):
        return Instances(self)
