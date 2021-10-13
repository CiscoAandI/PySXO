import requests
import base64
import logging
import json

from .decorators import cache

URI = '/be-console'

LOGGER = logging.getLogger(__name__)


class RequestHandler:
    AUTH_BASE = 'https://visibility.amp.cisco.com/iroh'
    MAX_PAGES = 99999
    BASE_URL = 'https://securex-ao.us.security.cisco.com'
    
    def __init__(self, client_id, client_password, cache, dry_run):
        self.cache = cache
        self.dry_run = dry_run
        self.client_id = client_id
        self.client_password = client_password
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            'Authorization': f'Bearer {self.jwt}'
        }
        self.params = {'limit': 100}
    
    def _get(self, **kwargs):
        LOGGER.info('Invoking _get function')
        return self._request(method='get', **kwargs)
    
    def _post(self, **kwargs):
        LOGGER.info('Invoking _post function')
        return self._request(method='post', **kwargs)

    def _request(self, method: str = 'get', paginated: bool = False, uri: str = URI, **kwargs):
        LOGGER.info('Invoking _request function:')
        if method != 'get' and self.dry_run:
            LOGGER.info(f"Dry run detected for non-get request, doing nothing.")
            return {}
        LOGGER.debug(f'\tMethod: {method}\n\tPaginated: {paginated}\n\tURI: {uri}\n\tKwargs:{kwargs}')
        # Setup request info
        kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}
        kwargs['params'] = {**self.params, **kwargs.get('params', {})}
        kwargs['url'] = f'{RequestHandler.BASE_URL}{uri}{kwargs["url"]}'
        
        LOGGER.info('Sending request')
        result = requests.request(method=method, **kwargs)
        LOGGER.info(f'Got response: {result}')

        if result.status_code == 401:
            LOGGER.info('Resetting cache due to 401')
            self._jwt = None     # must set to none to refresh cache
            self._token = None   # Same here, set to none to refresh cache
            self.headers['Authorization'] = f'Bearer {self.jwt}'
            kwargs['headers']['Authorization'] = self.headers['Authorization']

            LOGGER.info('Resending the request')
            LOGGER.debug(f'\tMethod: {method}\n\tPaginated: {paginated}\n\tURI: {uri}\n\tKwargs:{kwargs}')

            result = requests.request(method=method, **kwargs)
            LOGGER.info('Got response after resend')
        
        LOGGER.debug(f'Result:\n\t Headers:{json.dumps(dict(result.headers))}\n\tStatus_Code:{result.status_code}\n\tText:{result.text}')
        result.raise_for_status()

        if not paginated:
            LOGGER.info("Paginated is set to False so iterating over all pages to get all data.")
            LOGGER.debug(result.text)

            results = result.json().get('results', [])
            for i in range(RequestHandler.MAX_PAGES):
                if result.json().get('_links', {}).get('next'):
                    LOGGER.debug(f"Result.json()._links.next:{result.json().get('_links').get('next')}")
                    LOGGER.info(f"Getting page {i+2}")
                    kwargs.pop('url', None)
                    result = requests.request(
                        url=f"{RequestHandler.BASE_URL}{uri}{result.json()['_links']['next']}",
                        method=method,
                        **kwargs
                    )
                    results += result.json().get('results', [])
                else:
                    break
                        
            return results
        else:
            try:
                return result.json()
            except json.decoder.JSONDecodeError:
                LOGGER.error("Usually indicates a bad API route or bad credentials.")
                return result.text
    
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