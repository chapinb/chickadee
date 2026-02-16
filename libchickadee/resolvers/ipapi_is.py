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
