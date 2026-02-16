"""ipapi.is Resolver Tests."""

import copy
import unittest
from unittest.mock import patch

from libchickadee.resolvers.ipapi_is import Resolver

SAMPLE_RESPONSE_8888 = {
    "ip": "8.8.8.8",
    "rir": "ARIN",
    "is_bogon": False,
    "is_mobile": False,
    "is_crawler": False,
    "is_datacenter": True,
    "is_tor": False,
    "is_proxy": False,
    "is_vpn": False,
    "is_abuser": False,
    "company": {
        "name": "Google LLC",
        "domain": "google.com",
        "network": "8.8.8.0/24",
        "type": "hosting",
    },
    "asn": {
        "asn": 15169,
        "name": "GOOGLE",
        "org": "Google LLC",
        "network": "8.8.8.0/24",
    },
    "location": {
        "country": "United States",
        "city": "Mountain View",
        "state": "California",
        "latitude": 37.386,
        "longitude": -122.0838,
        "timezone": "America/Los_Angeles",
    },
}

SAMPLE_RESPONSE_1111 = {
    "ip": "1.1.1.1",
    "rir": "APNIC",
    "is_bogon": False,
    "is_mobile": False,
    "is_crawler": False,
    "is_datacenter": True,
    "is_tor": False,
    "is_proxy": False,
    "is_vpn": False,
    "is_abuser": False,
    "company": {
        "name": "Cloudflare Inc",
        "domain": "cloudflare.com",
        "network": "1.1.1.0/24",
        "type": "hosting",
    },
    "asn": {
        "asn": 13335,
        "name": "CLOUDFLARENET",
        "org": "Cloudflare Inc",
        "network": "1.1.1.0/24",
    },
    "location": {
        "country": "United States",
        "city": "San Francisco",
        "state": "California",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "timezone": "America/Los_Angeles",
    },
}


class MockResponse:
    """Generate mocked responses from the ipapi.is source."""

    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class IpapiIsTestCase(unittest.TestCase):
    """ipapi.is Resolver Tests."""

    def setUp(self):
        self.resolver = Resolver()

    def test_parse_response_success(self):
        """Verify normal response gets query field added."""
        data = copy.deepcopy(SAMPLE_RESPONSE_8888)
        result = self.resolver.parse_response("8.8.8.8", data)
        self.assertEqual(result["query"], "8.8.8.8")
        self.assertEqual(result["ip"], "8.8.8.8")

    def test_parse_response_flattens_nested_dicts(self):
        """Verify nested dicts are flattened to dot-notation keys."""
        data = copy.deepcopy(SAMPLE_RESPONSE_8888)
        result = self.resolver.parse_response("8.8.8.8", data)
        # Nested company fields should be flattened
        self.assertEqual(result["company.name"], "Google LLC")
        self.assertEqual(result["company.domain"], "google.com")
        self.assertEqual(result["company.type"], "hosting")
        # Nested asn fields should be flattened
        self.assertEqual(result["asn.asn"], 15169)
        self.assertEqual(result["asn.org"], "Google LLC")
        # Nested location fields should be flattened
        self.assertEqual(result["location.country"], "United States")
        self.assertEqual(result["location.city"], "Mountain View")
        self.assertEqual(result["location.timezone"], "America/Los_Angeles")
        # Parent dict keys should be removed
        self.assertNotIn("company", result)
        self.assertNotIn("asn", result)
        self.assertNotIn("location", result)

    def test_parse_response_error(self):
        """Verify error response returns failed record."""
        result = self.resolver.parse_response("999.999.999.999", {"error": "Invalid IP"})
        self.assertEqual(
            result,
            {
                "query": "999.999.999.999",
                "status": "failed",
                "message": "Invalid IP",
            },
        )

    @patch("libchickadee.resolvers.ipapi_is.requests.get")
    def test_single(self, mock_get):
        """Verify single() returns a parsed result with query field."""
        mock_get.return_value = MockResponse(json_data=copy.deepcopy(SAMPLE_RESPONSE_8888), status_code=200)
        self.resolver.data = "8.8.8.8"
        result = self.resolver.single()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["query"], "8.8.8.8")
        self.assertEqual(result[0]["ip"], "8.8.8.8")
        mock_get.assert_called_once()

    @patch("libchickadee.resolvers.ipapi_is.requests.post")
    def test_batch(self, mock_post):
        """Verify batch() handles dict-keyed response correctly."""
        batch_response = {
            "8.8.8.8": copy.deepcopy(SAMPLE_RESPONSE_8888),
            "1.1.1.1": copy.deepcopy(SAMPLE_RESPONSE_1111),
        }
        mock_post.return_value = MockResponse(json_data=batch_response, status_code=200)
        self.resolver.data = ["8.8.8.8", "1.1.1.1"]
        result = self.resolver.batch()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["query"], "8.8.8.8")
        self.assertEqual(result[1]["query"], "1.1.1.1")

    @patch("libchickadee.resolvers.ipapi_is.time.sleep")
    @patch("libchickadee.resolvers.ipapi_is.requests.get")
    def test_rate_limit_single(self, mock_get, mock_sleep):
        """Verify single() retries after 429 and sleeps 60s."""
        mock_get.side_effect = [
            MockResponse(json_data={}, status_code=429),
            MockResponse(json_data=copy.deepcopy(SAMPLE_RESPONSE_8888), status_code=200),
        ]
        self.resolver.data = "8.8.8.8"
        result = self.resolver.single()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["query"], "8.8.8.8")
        mock_sleep.assert_called_once_with(60)

    @patch("libchickadee.resolvers.ipapi_is.time.sleep")
    @patch("libchickadee.resolvers.ipapi_is.requests.post")
    def test_rate_limit_batch(self, mock_post, mock_sleep):
        """Verify batch() retries after 429 and sleeps 60s."""
        batch_response = {
            "8.8.8.8": copy.deepcopy(SAMPLE_RESPONSE_8888),
            "1.1.1.1": copy.deepcopy(SAMPLE_RESPONSE_1111),
        }
        mock_post.side_effect = [
            MockResponse(json_data={}, status_code=429),
            MockResponse(json_data=batch_response, status_code=200),
        ]
        self.resolver.data = ["8.8.8.8", "1.1.1.1"]
        result = self.resolver.batch()
        self.assertEqual(len(result), 2)
        mock_sleep.assert_called_once_with(60)


if __name__ == "__main__":
    unittest.main()
