import json
import time

import requests

from . import ResolverBase


__author__ = 'Chapin Bryce'
__date__ = 20190907
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class Resolver(ResolverBase):
    def __init__(self):
        super()
        self.uri = 'http://ip-api.com/'
        self.lang = "en"
        self.ratelimit = 150  # Requests per minute
        self.bulk_limit = 100  # Entries per request
        self.min_timeout = 60/self.ratelimit  # Minimum timeout period
        self.fields = [ # Ordered list of fields to gather
            'query',
            'as', 'org', 'isp'
            'continent', 'country', 'regionName', 'city',
            'district', 'zip',
            'mobile', 'proxy', 'reverse',
            'lat', 'lon', 'timezone'
            'status', 'message'
        ]

        self.data = None
        self.last_req = time.time()

    def batch(self):
        records = []
        for ip in self.data:
            records.append({'query': ip})

        for x in range(0, len(records), 100):
            self.sleeper()
            rdata = requests.post(
                self.uri+"batch",
                json=records[x:x+100],
                params={
                    'fields': ','.join(self.fields),
                    'lang': self.lang
                })
            self.last_req = time.time()
            for result in rdata.json():
                yield result
            

    def single(self):
        self.sleeper()
        rdata = requests.get(
            self.uri+"json/"+self.data,
            params={
                'fields': ','.join(self.fields),
                'lang': self.lang
        })
        self.last_req = time.time()
        yield rdata.json()
