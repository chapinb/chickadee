"""Chickadee

An application to provide context for an IP address

"""

import os
import json

import requests

class Resolve(object):
    def __init__(self):
        self.uri = 'http://ip-api.com/'
        self.ratelimit = (150/60)
        self.lang = "en"
        self.fields = [
            'status', 'message', 'continent', 'country',
            'regionName', 'city', 'district', 'zip', 'lat', 'lon',
            'timezone', 'isp', 'org', 'as', 'asname', 'reverse',
            'mobile', 'proxy'
        ]

        self.data = None

    def query(self, data):
        self.data = data
        if isinstance(data, list):
            yield self.batch()
        elif isinstance(data, str):
            yield self.single()
        else:
            raise NotImplementedError()

    def batch(self):
        records = []
        for ip in self.data:
            records.append({
                'query': ip,
                'fields': self.fields,
                'lang': self.lang
            })
        rdata = requests.get(self.uri+"batch", data=records)
        import pdb; pdb.set_trace()

    def single(self):
        rdata = requests.get(
            self.uri+"json/"+self.data, 
            params={
                'fields': self.fields,
                'lang': self.lang
        })
        import pdb; pdb.set_trace()
        