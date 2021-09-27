import requests
import base64

from .decorators import cache

URI = '/be-console/api'

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
        self.params = {
            'limit': 100
        }
    
    def _get(self, **kwargs):
        return self._request(method='get', **kwargs)
    
    def _post(self, **kwargs):
        return self._request(method='post', **kwargs)
    
    def _request(self, method='get', paginated=False, uri=URI, **kwargs):
        if method != 'get' and self.dry_run:
            return {}
        # refresh jwt
        kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}
        kwargs['params'] = {**self.params, **kwargs.get('params', {})}
        kwargs['url'] = f'{RequestHandler.BASE_URL}{uri}{kwargs["url"]}'
        result = requests.request(method=method, **kwargs)
        if result.status_code == 401:
            # Reset cache
            self._jwt = None
            self._token = None
            self.headers['Authorization'] = f'Bearer {self.jwt}'
            kwargs['headers']['Authorization'] = self.headers['Authorization']
            result = requests.request(method=method, **kwargs)
        result.raise_for_status()
        
        if not paginated:
            results = result.json().get('results', [])
            for i in range(RequestHandler.MAX_PAGES):
                if result.json().get('_links', {}).get('next'):
                    # TODO: logger
                    # print(result.json().get('_links').get('next'))
                    # print(f"Getting page: {i + 2}")
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
                # Usually indicates a bad API route or bad credentials.
                return result.text
    
    @property
    @cache('_token')
    def token(self):
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