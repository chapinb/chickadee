"""XLSX parsing tests."""
import unittest
import os

from libchickadee.parsers.xlsx import XLSXParser

__author__ = 'Chapin Bryce'
__date__ = 20190915
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

class XLSXParserTestCase(unittest.TestCase):
    """XLSX parsing tests."""
    def setUp(self):
        """Test Config."""
        self.test_data_ips = {
            '10.0.1.2', '8.8.8.8', '1.1.1.1', '2.2.2.2', '4.4.4.4',
            '2001:4860:4860::8844', '2001:4860:4860::8888'
        }
        self.parser = XLSXParser()
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), 'test_data')

    def test_ip_extraction_xlsx(self):
        """Extraction test."""
        self.parser.parse_file(self.test_data_dir+'/test_ips.xlsx')
        self.assertEqual(self.test_data_ips, self.parser.ips)

if __name__ == '__main__':
    unittest.main()
