import requests

from mope.__version__ import __version__
from mope.resources.shop import ShopResource


class Mope:
    def __init__(self, token=None):
        self._token = token
        self._headers = {}
        self.url_base = 'https://api.mope.sr/api'

        self._make_headers(token, user_agent='Python Mope %s' % __version__)

        self.shop = ShopResource(self)

    def _make_headers(self, token, user_agent):
        self._headers = {
            'User-Agent': user_agent,
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token,
        }

    def call_api(self, method, endpoint, params=None, data=None, json=None):
        return requests.request(method=method, url=endpoint, params=params, data=data, json=json, headers=self._headers)

    def __str__(self):
        return 'Python Mope %s' % __version__
