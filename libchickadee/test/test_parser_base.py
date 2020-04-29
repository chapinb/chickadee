"""Plain-text parsing tests"""
import unittest

from libchickadee.parsers import ParserBase

__author__ = 'Chapin Bryce'
__date__ = 20200301
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class ParserBaseTestCase(unittest.TestCase):
    def test_ipv6(self):
        ip = "2001:4860:4860::8844%16"
        bare_ip = ParserBase.strip_ipv6(ip)
        self.assertEqual(ip.split("%")[0], bare_ip)

    def test_bogon_ipv4(self):
        ip_list = ['10.1.1.1', '192.168.1.1', '127.0.0.1',
                   '172.16.1.1', '0.0.0.0', '100.64.1.1',
                   '169.254.1.1', '192.0.0.23', '192.0.2.1',
                   '198.18.0.22', '198.51.100.1', '203.0.113.45',
                   '224.0.0.1', '240.0.2.0', '255.255.255.255']
        for ip in ip_list:
            self.assertTrue(ParserBase.is_bogon(ip))

    def test_nonbogon_ipv4(self):
        ip_list = ['1.1.1.1', '192.169.1.1', '172.36.1.1',
                   '198.51.101.1']
        for ip in ip_list:
            self.assertFalse(ParserBase.is_bogon(ip))

    def test_bogon_ipv6(self):
        ip_list = [
            "fe80::175:a2ad:8508:a655",
            "fec0::517b:deaa:fb23:5013",
            "fe00::517b:deaa:fb23:5013",
            "ff00::517b:deaa:fb23:5013",
            "100::517b:deaa:fb23:5013"
        ]
        for ip in ip_list:
            self.assertTrue(ParserBase.is_bogon(ip))

    def test_nonbogon_ipv6(self):
        ip_list = [
            "2607:f8b0:4006:803::200e",
            "2a03:2880:f112:83:face:b00c:0:25de",
            '2001:4860:4860::8844',
            '2001:4860:4860::8888',
            '2001:4860:4860:0:0:0:0:8844',
            '2001:4860:4860:0:0:0:0:8888'
        ]
        for ip in ip_list:
            self.assertFalse(ParserBase.is_bogon(ip))

    def test_check_ips_nobogon(self):
        parser = ParserBase()
        parser.ips = {}
        ip = [
            "2001:4860:4860::8844",
            "fe80::175:a2ad:8508:a655%16",
            '1.1.1.1',
            '127.0.0.1',
            '1.1.1.1'
        ]
        parser.check_ips(",".join(ip))
        self.assertDictEqual(
            parser.ips,
            {
                "2001:4860:4860::8844": 1,
                '1.1.1.1': 2
            }
        )

    def test_check_ips_bogon(self):
        parser = ParserBase(ignore_bogon=False)
        parser.ips = {}
        ip = [
            "2001:4860:4860::8844",
            "fe80::175:a2ad:8508:a655%16",
            '1.1.1.1',
            '127.0.0.1',
            '1.1.1.1'
        ]
        parser.check_ips(",".join(ip))
        self.assertDictEqual(
            parser.ips,
            {
                "2001:4860:4860::8844": 1,
                "fe80::175:a2ad:8508:a655": 1,
                '127.0.0.1': 1,
                '1.1.1.1': 2
            }
        )


if __name__ == '__main__':
    unittest.main()
