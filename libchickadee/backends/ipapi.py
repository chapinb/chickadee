"""Backend leveraging the ip-api.com JSON API."""
import logging
import time
from datetime import datetime, timedelta

import requests
from tqdm import trange

from . import ResolverBase

logger = logging.getLogger('libchickadee.chickadee')

__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

FIELDS = [  # Ordered list of fields to gather
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
        ResolverBase.__init__(self, fields=fields, lang='en')

        self.uri = 'http://ip-api.com/'
        self.api_key = None
        self.enable_sleep = True
        self.wait_time = datetime.now()

    def rate_limit(self, headers):
        """Method to check rate limiting."""
        if int(headers.get('X-Rl', '0')) < 1:
            self.wait_time = datetime.now() + \
                timedelta(seconds=int(headers.get('X-Ttl', '0'))+1)

    def sleeper(self):
        """Method to sleep operations for rate limiting."""
        while True:
            now = datetime.now()
            wait_time = self.wait_time - now
            if wait_time.total_seconds() < 0:
                self.wait_time = datetime.now()
                return
            wt_sec = wait_time.total_seconds()+1  # add a buffer
            logger.info(
                'Sleeping for {} seconds due to rate limiting.'.format(wt_sec))
            time.sleep(wt_sec)

    def batch(self):
        """Handle batch query operations."""
        records = []
        for ip in self.data:
            records.append({'query': ip})

        resolved_recs = []
        if self.pbar:
            orig_recs = trange(0, len(records), 100,
                               desc="Resolving IPs", unit_scale=True)
        else:
            orig_recs = range(0, len(records), 100)

        for x in orig_recs:
            params = {
                'fields': ','.join(self.fields),
                'lang': self.lang,
            }
            if self.api_key:
                params['key'] = self.api_key

            if self.enable_sleep:
                self.sleeper()

            rdata = requests.post(
                self.uri+"batch",
                json=records[x:x+100],
                params=params
            )

            if rdata.status_code == 200:
                self.rate_limit(rdata.headers)
                result_list = [x for x in rdata.json()]
                resolved_recs += result_list
            elif rdata.status_code == 429:
                self.rate_limit(rdata.headers)
                self.sleeper()
                return self.batch()
            else:
                msg = "Unknown error encountered: {}".format(rdata.status_code)
                logger.error(msg)
                result_list = []
                for result in records[x:x+100]:
                    result_list.append({'query': result,
                                        'status': 'failed',
                                        'message': msg})
                resolved_recs += result_list
        return resolved_recs

    def single(self):
        """Handle single item query operations."""
        params = {
            'fields': ','.join(self.fields),
            'lang': self.lang,
        }
        if self.api_key:
            params['key'] = self.api_key

        if self.enable_sleep:
            self.sleeper()

        rdata = requests.get(
            self.uri+"json/"+self.data,
            params=params
        )
        if rdata.status_code == 200:
            self.rate_limit(rdata.headers)
            return rdata.json()
        elif rdata.status_code == 429:
            self.rate_limit(rdata.headers)
            self.sleeper()
            return self.single()
        else:
            msg = "Unknown error encountered: {}".format(rdata.status_code)
            logger.error(msg)
            return [{'query': self.data, 'status': 'failed', 'message': msg}]


class ProResolver(Resolver):
    """GeoIP resolver using the ip-api.com paid subscription."""
    def __init__(self, api_key, fields=FIELDS, lang='en'):
        Resolver.__init__(self, fields=fields, lang='en')
        self.uri = 'https://pro.ip-api.com/'
        self.api_key = api_key
        self.enable_sleep = False
        logger.info("API key found.")
