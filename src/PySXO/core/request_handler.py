import requests
import base64
import logging
import json

from requests import Response
from typing import Dict, List, Union

from .decorators import cache


URI = '/be-console'

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class RequestHandler:
    AUTH_BASE = 'https://visibility.amp.cisco.com/iroh'
    MAX_PAGES = 99999
    BASE_URL = 'https://securex-ao.us.security.cisco.com'
    
    def __init__(self, client_id: str, client_password: str, cache, dry_run):
        self.cache = cache
        self.dry_run = dry_run
        self.client_id = client_id
        self.client_password = client_password
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            'Authorization': f'Bearer {self.jwt}'
        }
        self.params = {
            'limit': 100
        }
    
    def _get(self, **kwargs) -> Union[List, Dict]:
        LOGGER.info('Invoking _get function')
        return self._request(method='get', **kwargs)
    
    def _post(self, **kwargs) -> Union[List, Dict]:
        LOGGER.info('Invoking _post function')
        return self._request(method='post', **kwargs)

    def _request(self, method: str = 'get', uri: str = URI, **kwargs) -> Union[List, Dict]:
        
        if method != 'get' and self.dry_run:
            return {}

        kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}
        kwargs['url'] = f'{RequestHandler.BASE_URL}{uri}{kwargs["url"]}'
        
        LOGGER.debug(json.dumps(dict(kwargs)))
        LOGGER.info(f"Making a {method.upper()} requests to {kwargs['url']} ")

        response = requests.request(method=method, **kwargs)
          
        if response.status_code == 401:
            response = self._renew_token_and_retry()

        response.raise_for_status()

        return response.json()

    def _paginated_request(self, **kwargs) -> List[Union[List, Dict]]:
        kwargs['params'] = {**self.params, **kwargs.get('params', {})}
        page = 1 
        while kwargs["url"]:
            print(kwargs)
            LOGGER.info(f"Getting page {page}")
            response = self._post(
                **kwargs
            )
            kwargs["params"] = {}
            kwargs["url"] = response.get('_links', False).get('next', False)
            yield response.get('results',[])
    
    def _renew_token_and_retry(self, method: str='get', **kwargs: dict) -> Response:
            self._jwt = None
            self._token = None
            self.headers['Authorization'] = f'Bearer {self.jwt}'
            kwargs['headers']['Authorization'] = self.headers['Authorization']

            return requests.request(method=method, **kwargs)
    
    @property
    @cache('_token')
    def token(self):
        LOGGER.info("Posting for token")
        result = requests.post(
            url=f"{RequestHandler.AUTH_BASE}/oauth2/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                'Authorization': 'Basic ' + base64.standard_b64encode(f'{self.client_id}:{self.client_password}'.encode()).decode()
            },
            data="grant_type=client_credentials"
        )
        result.raise_for_status()
        return result.json()['access_token']

    @property
    @cache('_jwt')
    def jwt(self):
        LOGGER.info('Posting for JWT')
        result = requests.post(
            url=f"{RequestHandler.AUTH_BASE}/ao/gen-jwt",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                'Authorization': f'Bearer {self.token}'
            },
            data="{}"
        )
        result.raise_for_status()
        return result.json()