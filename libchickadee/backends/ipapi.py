"""Backend leveraging the ip-api.com JSON API."""
import logging
import time

import requests

from . import ResolverBase

logger = logging.getLogger('libchickadee.chickadee')

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

        self.uri = 'http://ip-api.com/'
        self.api_key = None
        self.enable_sleep = True

    @staticmethod
    def sleeper(headers):
        """Method to sleep operations for rate limiting."""
        if int(headers['X-Rl']) < 1:
            logger.info('Sleeping due to rate limiting.')
            time.sleep(int(headers['X-Ttl'])+1)

    def batch(self):
        """Handle batch query operations."""
        records = []
        for ip in self.data:
            records.append({'query': ip})

        for x in range(0, len(records), 100):
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

            if rdata.status_code == 200:
                result_list = []
                for result in rdata.json():
                    result_list.append(result)
                return result_list

            else:
                msg = "Unknown error encountered: {}".format(rdata.status_code())
                logger.error(msg)
                result_list = []
                for result in records[x:x+100]:
                    result_list.append({'query': result,
                                        'status': 'failed',
                                        'message': msg})
                return result_list

    def single(self):
        """Handle single item query operations."""
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
        if rdata.status_code == 200:
            self.sleeper(rdata.headers)
            return [rdata.json()]

        else:
            msg = "Unknown error encountered: {}".format(rdata.status_code())
            logger.error(msg)
            return [{'query': self.data, 'status': 'failed', 'message': msg}]

class ProResolver(Resolver):
    """GeoIP resolver using the ip-api.com paid subscription."""
    def __init__(self, api_key, fields=FIELDS, lang='en'):
        Resolver.__init__(self, fields=None, lang='en')
        self.uri = 'https://pro.ip-api.com/'
        self.api_key = api_key
        self.enable_sleep = False
