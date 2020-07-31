"""Plain-text parsing tests"""
import unittest
import os

from libchickadee.parsers.plain_text import PlainTextParser

__author__ = 'Chapin Bryce'
__date__ = 20200107
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class PlainTextParserTestCase(unittest.TestCase):
    """Plain-text parsing tests"""
    def setUp(self):
        """Test config"""
        self.test_data_ips = {
            '10.0.1.2': 1,
            '8.8.8.8': 1,
            '1.1.1.1': 2,
            '2.2.2.2': 1,
            '4.4.4.4': 1,
            '2001:4860:4860::8844': 1,
            '2001:4860:4860::8888': 1,
            '2001:4860:4860:0:0:0:0:8844': 1,
            '2001:4860:4860:0:0:0:0:8888': 1
        }
        self.parser = PlainTextParser(ignore_bogon=False)
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), 'test_data')

    def test_ip_extraction_txt(self):
        """Test text file extraction"""
        self.parser.parse_file(os.path.join(self.test_data_dir, 'txt_ips.txt'))
        self.assertEqual(self.test_data_ips, self.parser.ips)

    def test_ip_extraction_gz(self):
        """Test GZ Text file extraction"""
        self.parser.parse_file(self.test_data_dir+'/txt_ips.txt.gz')
        self.assertEqual(self.test_data_ips, self.parser.ips)

    def test_gz_gzip_detection(self):
        """Test GZ detection"""
        self.assertTrue(
            self.parser.is_gz_file(self.test_data_dir+'/txt_ips.txt.gz')
        )

    def test_gz_txt_detection(self):
        """Test GZ detection"""
        self.assertFalse(
            self.parser.is_gz_file(self.test_data_dir+'/txt_ips.txt')
        )


if __name__ == '__main__':
    unittest.main()
