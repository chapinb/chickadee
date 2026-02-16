"""
IPAPI.is Resolver
=================

Resolver leveraging the ipapi.is JSON API.

This is a third-party data source that provides GeoIP, ASN, company,
and threat intelligence information for IPv4 and IPv6 addresses.

Data Source Information
-----------------------

This data source is hosted at ipapi.is and requires an internet connection
to use. It offers a free API, with terms described on their site. Please refer
to the service's website for an authoritative source on API specifications.
This documentation summarizes a point in time understanding of the data source
though since it is a third party service, it may change in a manner that breaks
this tool or causes this documentation to become inaccurate. In no way is
inclusion of a data source in libchickadee an endorsement of the data source.

**Data source documentation:** https://ipapi.is/developers.html

Endpoints
^^^^^^^^^

The API supports JSON responses for both single and batch lookups.

* Single: ``GET https://api.ipapi.is?q={ip}``
* Batch: ``POST https://api.ipapi.is`` with JSON body ``{"ips": [...]}``

Fields
^^^^^^

These fields are in no particular order. Nested fields use dot notation.

* query
* count
* ip
* rir
* is_bogon
* is_mobile
* is_crawler
* is_datacenter
* is_tor
* is_proxy
* is_vpn
* is_abuser
* company.name
* company.domain
* company.network
* company.type
* asn.asn
* asn.name
* asn.org
* asn.network
* location.country
* location.city
* location.state
* location.latitude
* location.longitude
* location.timezone
* status
* message

Limitations
^^^^^^^^^^^

The free tier allows 1,000 requests per day with no authentication required.
Rate limiting returns HTTP 429 with no rate limit headers; a fixed 60-second
backoff is used on 429 responses.

The professional service supports an API key passed as ``key`` in query
parameters (GET) or in the POST body alongside the ``ips`` list.

Module Documentation
--------------------

"""

import logging
import time

import requests
from tqdm import trange

from . import ResolverBase

logger = logging.getLogger(__name__)

FIELDS = [
    "query",
    "count",
    "ip",
    "rir",
    "is_bogon",
    "is_mobile",
    "is_crawler",
    "is_datacenter",
    "is_tor",
    "is_proxy",
    "is_vpn",
    "is_abuser",
    "company.name",
    "company.domain",
    "company.network",
    "company.type",
    "asn.asn",
    "asn.name",
    "asn.org",
    "asn.network",
    "location.country",
    "location.city",
    "location.state",
    "location.latitude",
    "location.longitude",
    "location.timezone",
    "status",
    "message",
]


class Resolver(ResolverBase):
    """Class to handle ipapi.is API queries for IP addresses.

    Sets endpoint to the free API and configures rate limit sleep timers.

    Args:
        fields (list): Collection of fields to request in resolution.
        lang (str): Language for returned results.
    """

    def __init__(self, fields=None, lang="en"):
        """Initialize class object and configure default values."""
        super().__init__()
        self.lang = lang
        self.fields = FIELDS if not fields else fields
        self.uri = "https://api.ipapi.is"
        self.api_key = None
        self.enable_sleep = True

    def sleeper(self):
        """Fixed 60-second sleep for rate limiting.

        The ipapi.is API does not provide rate limit headers, so a fixed
        backoff period is used when a 429 response is received.

        Return:
            None
        """
        logger.info("Sleeping for 60 seconds due to rate limiting.")
        time.sleep(60)

    def parse_response(self, ip, json_data):
        """Parse a single IP response from ipapi.is.

        Checks for error responses (HTTP 200 with ``{"error": "..."}`` body)
        and returns a failed record if found. Otherwise returns the response
        dict with ``query`` set to the requested IP.

        Args:
            ip (str): The requested IP address.
            json_data (dict): The JSON response body for this IP.

        Returns:
            (dict): Parsed record with ``query`` field set.
        """
        if "error" in json_data:
            return {"query": ip, "status": "failed", "message": json_data["error"]}
        json_data["query"] = ip
        return json_data

    def single(self):
        """Handle single item query operations.

        Generally not called directly, should be called by ``self.query()`` to
        allow for the logic to handle which endpoint is preferred.

        Returns:
            (list): List of resolved IP address records with specified fields.
        """
        params = {"q": self.data}
        if self.api_key:
            params["key"] = self.api_key

        rdata = requests.get(self.uri, params=params, timeout=60)
        if rdata.status_code == 200:
            return [self.parse_response(self.data, rdata.json())]
        if rdata.status_code == 429 and self.enable_sleep:
            self.sleeper()
            return self.single()
        msg = f"Unknown error encountered: {rdata.status_code}"
        logger.error(msg)
        return [{"query": self.data, "status": "failed", "message": msg}]
