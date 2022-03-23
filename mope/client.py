from urllib.parse import urljoin

import requests

from mope.__version__ import __version__
from mope.resources.shop import ShopResource

_user_agent = 'Python Mope %s' % __version__


class Client:
    def __init__(self, token):
        self._token = token
        self._headers = {
            'User-Agent': _user_agent,
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token,
        }
        self._base_url = 'https://api.mope.sr/api'

    def call_api(self, method, endpoint, params=None, data=None, json=None):
        url = urljoin(self._base_url, endpoint)
        return requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=self._headers,
        )


class Mope:
    def __init__(self, token=None):
        self._token = token
        self._headers = {
            'User-Agent': _user_agent,
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token,
        }
        self.base_url = 'https://api.mope.sr/api'

        self._client = Client(token)

        self.shop = ShopResource(self._client)

    def __str__(self):
        return _user_agent
