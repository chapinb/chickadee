"""IP-API Backend Tests."""
import unittest
import csv
import json
import os
from collections import OrderedDict

from libchickadee.backends.ipapi import Resolver

__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class IPAPITestCase(unittest.TestCase):
    """IP-API Backend Tests."""
    def setUp(self):
        """Test config"""
        self.test_data_ips = [
            '10.0.1.2', '8.8.8.8', '2001:4860:4860::8888'
        ]
        self.expected_result = [
            {'query': '10.0.1.2'},

            {'as': 'AS15169 Google LLC', 'country': 'United States',
             'org': 'Level 3', 'proxy': False, 'query': '8.8.8.8'},

            {'as': 'AS15169 Google LLC', 'country': 'United States',
             'org': 'Google LLC', 'proxy': False,
             'query': '2001:4860:4860::8888'}
        ]
        self.resolver = Resolver(fields=['query', 'count', 'as',
                                         'country', 'org', 'proxy'])

    def test_ipapi_resolve_query_single(self):
        """Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            data = self.resolver.query(ip)
            self.assertEqual(data, self.expected_result[count])

    def test_ipapi_resolve_query_batch(self):
        """Batch Query Method Test"""
        data = self.resolver.query(self.test_data_ips)
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.expected_result:
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_single(self):
        """Single Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            self.resolver.data = ip
            data = self.resolver.single()
            self.assertEqual(data, self.expected_result[count])

    def test_ipapi_resolve_batch(self):
        """Batch Query Method Test"""
        self.resolver.data = self.test_data_ips
        data = self.resolver.batch()
        res = [x for x in data]
        self.assertCountEqual(res, self.expected_result)

    def test_ipapi_resolve_single_field(self):
        """Single Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            self.resolver.data = ip
            self.resolver.fields = ['query', 'country', 'as']
            data = self.resolver.single()

            expected = {}
            for field in ['query', 'country', 'as']:
                if field not in data:
                    continue
                expected[field] = self.expected_result[count].get(field, None)
            self.assertEqual(data, expected)

    def test_ipapi_rate_limiting(self):
        for x in range(20):
            for count, ip in enumerate(self.test_data_ips):
                data = self.resolver.query(ip)
                self.assertEqual(data, self.expected_result[count])


class WritersTestCase(unittest.TestCase):
    def setUp(self):
        self.data = [
            OrderedDict(**{"a": '1', "b": "2"})
        ]
        self.testfile = "testfile"
        self.open_file = None

    def tearDown(self):
        self.open_file.close()
        os.remove(self.testfile)

    def test_write_csv(self):
        Resolver.write_csv(self.testfile, self.data)
        self.open_file = open("testfile")
        read_data = next(csv.DictReader(self.open_file))
        self.assertDictEqual(
            self.data[0],
            read_data
        )

    def test_write_json(self):
        data = [
            {"a": '1', "b": "2"}
        ]
        Resolver.write_json(self.testfile, self.data)
        self.open_file = open("testfile")
        read_data = json.load(self.open_file)
        self.assertEqual(
            data,
            read_data
        )

    def test_write_json_headers(self):
        Resolver.write_json(self.testfile, self.data, ['a', 'none'])
        self.open_file = open("testfile")
        read_data = json.load(self.open_file)
        rec = self.data[0]
        rec.pop("b")
        rec["none"] = None
        self.assertDictEqual(
            rec,
            read_data[0]
        )

    def test_write_json_lines(self):
        Resolver.write_json(self.testfile, self.data, lines=True)
        self.open_file = open("testfile")
        read_data = json.load(self.open_file)
        self.assertDictEqual(
            self.data[0],
            read_data
        )


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
