"""IP-API Backend Tests."""
import unittest

from libchickadee.backends.ipapi import Resolver

__author__ = 'Chapin Bryce'
__date__ = 20190927
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

class IPAPITestCase(unittest.TestCase):
    """IP-API Backend Tests."""
    def setUp(self):
        """Test config"""
        self.test_data_ips = [
            '10.0.1.2', '8.8.8.8', '1.1.1.1', '2.2.2.2', '2001:4860:4860::8888'
        ]
        self.expected_result = [
            {'message': 'private range', 'query': '10.0.1.2'},

            {'as': 'AS15169 Google LLC', 'city': 'Ashburn',
             'country': 'United States', 'district': '', 'lat': 39.0438,
             'lon': -77.4874, 'mobile': False, 'org': 'Google Inc.',
             'proxy': False, 'query': '8.8.8.8', 'reverse': 'dns.google',
             'regionName': 'Virginia', 'zip': '20149'},

            {'as': 'AS13335 Cloudflare, Inc.', 'city': 'Sydney',
             'country': 'Australia', 'district': '', 'lat': -33.8688,
             'lon': 151.209, 'mobile': False, 'org': '', 'proxy': False,
             'query': '1.1.1.1', 'regionName': 'New South Wales',
             'zip': '1001', 'reverse': 'one.one.one.one'},

            {'as': 'AS3215 Orange S.A.', 'city': 'Aubervilliers',
             'country': 'France', 'district': '', 'lat': 48.9123,
             'lon': 2.38405, 'mobile': False, 'org': '', 'proxy': True,
             'query': '2.2.2.2', 'regionName': 'Île-de-France',
             'zip': '93300', 'reverse': ''},

            {'as': 'AS15169 Google LLC', 'city': 'Newark',
             'country': 'United States', 'district': '', 'lat': 40.7357,
             'lon': -74.1724, 'mobile': False, 'org': 'Google LLC',
             'proxy': False, 'query': '2001:4860:4860::8888',
             'regionName': 'New Jersey', 'zip': '07175',
             'reverse': 'dns.google',}
        ]
        self.resolver = Resolver()

    def test_ipapi_resolve_query_single(self):
        """Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            data = self.resolver.query(ip)
            res = [x for x in data]
            self.assertEqual(res, [self.expected_result[count]])

    def test_ipapi_resolve_query_batch(self):
        """Batch Query Method Test"""
        data = self.resolver.query(self.test_data_ips)
        res = [x for x in data]
        batch_result = [] # No reverse field
        for item in self.expected_result:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_single(self):
        """Single Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            self.resolver.data = ip
            data = self.resolver.single()
            res = [x for x in data]
            self.assertEqual(res, [self.expected_result[count]])

    def test_ipapi_resolve_batch(self):
        """Batch Query Method Test"""
        self.resolver.data = self.test_data_ips
        data = self.resolver.batch()
        res = [x for x in data]
        batch_result = [] # No reverse field
        for item in self.expected_result:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)


    def test_ipapi_resolve_single_field(self):
        """Single Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            self.resolver.data = ip
            self.resolver.fields = ['query', 'country', 'as']
            data = self.resolver.single()
            res = [x for x in data]

            expected = {}
            for field in ['query', 'country', 'as', 'message']:
                if field not in res[0]:
                    continue
                expected[field] = self.expected_result[count].get(field, None)
            self.assertEqual(res, [expected])


'''
import os
from libchickadee.backends.ipapi import ProResolver
# Disabled - Unit test only run locally due to use of API key
class IPAPIProTestCase(unittest.TestCase):
    """IP-API Backend Tests."""
    def setUp(self):
        """Test config"""
        self.test_data_ips = [
            '10.0.1.2', '8.8.8.8', '1.1.1.1', '2.2.2.2', '2001:4860:4860::8888'
        ]
        self.expected_result = [
            {'message': 'private range', 'query': '10.0.1.2'},

            {'as': 'AS15169 Google LLC', 'city': 'Ashburn',
             'country': 'United States', 'district': '', 'lat': 39.0438,
             'lon': -77.4874, 'mobile': False, 'org': 'Google Inc.',
             'proxy': False, 'query': '8.8.8.8', 'reverse': 'dns.google',
             'regionName': 'Virginia', 'zip': '20149'},

            {'as': 'AS13335 Cloudflare, Inc.', 'city': 'Sydney',
             'country': 'Australia', 'district': '', 'lat': -33.8688,
             'lon': 151.209, 'mobile': False, 'org': '', 'proxy': False,
             'query': '1.1.1.1', 'regionName': 'New South Wales',
             'zip': '1001', 'reverse': 'one.one.one.one'},

            {'as': 'AS3215 Orange S.A.', 'city': 'Aubervilliers',
             'country': 'France', 'district': '', 'lat': 48.9123,
             'lon': 2.38405, 'mobile': False, 'org': '', 'proxy': True,
             'query': '2.2.2.2', 'regionName': 'Île-de-France',
             'zip': '93300', 'reverse': ''},

            {'as': 'AS15169 Google LLC', 'city': 'Newark',
             'country': 'United States', 'district': '', 'lat': 40.7357,
             'lon': -74.1724, 'mobile': False, 'org': 'Google LLC',
             'proxy': False, 'query': '2001:4860:4860::8888',
             'regionName': 'New Jersey', 'zip': '07175',
             'reverse': 'dns.google',}
        ]
        self.resolver = ProResolver(os.environ.get('CHICKADEE_API_KEY', ''))

    def test_ipapi_resolve_query_single(self):
        """Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            data = self.resolver.query(ip)
            res = [x for x in data]
            self.assertEqual(res, [self.expected_result[count]])

    def test_ipapi_resolve_query_batch(self):
        """Batch Query Method Test"""
        data = self.resolver.query(self.test_data_ips)
        res = [x for x in data]
        batch_result = [] # No reverse field
        for item in self.expected_result:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_single(self):
        """Single Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            self.resolver.data = ip
            data = self.resolver.single()
            res = [x for x in data]
            self.assertEqual(res, [self.expected_result[count]])

    def test_ipapi_resolve_batch(self):
        """Batch Query Method Test"""
        self.resolver.data = self.test_data_ips
        data = self.resolver.batch()
        res = [x for x in data]
        batch_result = [] # No reverse field
        for item in self.expected_result:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)
# '''

if __name__ == '__main__':
    unittest.main()
