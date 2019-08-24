"""Chickadee

An application to provide context for an IP address

"""

import os
import json

import requests

class Resolver(object):
    def __init__(self):
        self.uri = 'http://ip-api.com/'
        self.ratelimit = (150/60)
        self.lang = "en"
        self.fields = [ # Ordered list of fields to gather
            'query',
            'as', 'org', 'isp'
            'continent', 'country', 'regionName', 'city', 'district', 'zip',
            'mobile', 'proxy', 'reverse',
            'lat', 'lon', 'timezone'
            'status', 'message'
        ]

        self.data = None
        self.last_request

    def query(self, data):
        self.data = data
        if isinstance(data, (list, tuple, set)):
            return self.batch()
        elif isinstance(data, str):
            return self.single()
        else:
            raise NotImplementedError()

    def batch(self):
        records = []
        for ip in self.data:
            records.append({'query': ip})
        rdata = requests.post(
            self.uri+"batch",
            json=records,
            params={
                'fields': ','.join(self.fields),
                'lang': self.lang
            })
        yield rdata.json()

    def single(self):
        rdata = requests.get(
            self.uri+"json/"+self.data,
            params={
                'fields': ','.join(self.fields),
                'lang': self.lang
        })
        yield rdata.json()

if __name__ == "__main__":
    import argparse
    import pprint
    parser = argparse.ArgumentParser()
    parser.add_argument('ips', help='Comma separated list of IPs')
    args = parser.parse_args()

    resolver = Resolver()
    if ',' in args.ips:
        ip_data = args.ips.split(',')
    else:
        ip_data = args.ips

    results = resolver.query(ip_data)

    all_results = [x for x in results][0]
    pprint.pprint(all_results)
