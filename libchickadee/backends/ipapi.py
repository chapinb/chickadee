"""Backend leveraging the ip-api.com JSON API."""
import time

import requests

from . import ResolverBase


__author__ = 'Chapin Bryce'
__date__ = 20190927
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

FIELDS = [ # Ordered list of fields to gather
    'query',
    'as', 'org', 'isp'
    'continent', 'country', 'regionName', 'city',
    'district', 'zip',
    'mobile', 'proxy', 'reverse',
    'lat', 'lon', 'timezone'
    'status', 'message'
]

class Resolver(ResolverBase):
    """Class to handle ip-api.com API queries for IP addresses."""
    def __init__(self, fields=FIELDS, lang='en'):
        self.supported_langs = [
            'en', 'de', 'es', 'pt-BR', 'fr', 'ja', 'zh-CN', 'ru'
        ]
        if lang not in self.supported_langs:
            lang = 'en'
        ResolverBase.__init__(self, fields=FIELDS, lang='en')

        self.ratelimit = 150  # Requests per minute
        self.bulk_limit = 100  # Entries per request
        self.min_timeout = 60/self.ratelimit  # Minimum timeout period
        self.uri = 'http://ip-api.com/'
        self.api_key = None
        self.enable_sleep = True

    def batch(self):
        """Handle batch query operations."""
        records = []
        for ip in self.data:
            records.append({'query': ip})

        for x in range(0, len(records), 100):
            if self.enable_sleep:
                self.sleeper()
            params = {
                'fields': ','.join(self.fields),
                'lang': self.lang,
            }
            if self.api_key:
                params['key'] = self.api_key
            rdata = requests.post(
                self.uri+"batch",
                json=records[x:x+100],
                params=params
            )
            if self.enable_sleep:
                self.last_req = time.time()
            for result in rdata.json():
                yield result

    def single(self):
        """Handle single item query operations."""
        if self.enable_sleep:
            self.sleeper()
        params = {
            'fields': ','.join(self.fields),
            'lang': self.lang,
        }
        if self.api_key:
            params['key'] = self.api_key
        rdata = requests.get(
            self.uri+"json/"+self.data,
            params=params
        )
        if self.enable_sleep:
            self.last_req = time.time()
        yield rdata.json()


class ProResolver(Resolver):
    """GeoIP resolver using the ip-api.com paid subscription."""
    def __init__(self, api_key, fields=FIELDS, lang='en'):
        Resolver.__init__(self, fields=None, lang='en')
        self.uri = 'https://pro.ip-api.com/'
        self.api_key = api_key
        self.enable_sleep = False
