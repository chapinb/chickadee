"""VirusTotal Resolver Tests."""
import unittest
import json
import os

from libchickadee.resolvers.virustotal import ProResolver

__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class IPAPITestCase(unittest.TestCase):
    """VirusTotal Resolver Tests."""
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
        self.resolver = ProResolver(api_key='')
        local_dir = os.path.abspath(__file__).rsplit(os.sep, 1)[0]
        resource_file = open(os.path.join(local_dir, 'vt_resp_data.json'))
        self.vt_rep_data_list = json.load(resource_file)
        resource_file.close()

    def test_parse_vt_resp(self):
        vt_resp_data = self.vt_rep_data_list["Test0"]["test"]
        query = self.vt_rep_data_list["Test0"]["query"]
        expected = self.vt_rep_data_list["Test0"]["expected"]
        vt_values = self.resolver.parse_vt_resp(query, vt_resp_data)
        self.assertDictEqual(vt_values, expected)

    def test_parse_vt_resp_2(self):
        vt_resp_data = self.vt_rep_data_list["Test1"]["test"]
        query = self.vt_rep_data_list["Test1"]["query"]
        expected = self.vt_rep_data_list["Test1"]["expected"]
        vt_values = self.resolver.parse_vt_resp(query, vt_resp_data)
        self.assertDictEqual(vt_values, expected)


if __name__ == "__main__":
    unittest.main()
