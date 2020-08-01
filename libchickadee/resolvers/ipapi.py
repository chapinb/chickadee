"""
IP-API Resolver
===============

Resolver leveraging the ip-api.com JSON API.

This is a third-party data source that provides GeoIP, ASN, Organization,
ISP, and other resolution information for IPv4 and IPv6 addresses.

Data Source Information
-----------------------

This data source is hosted at ip-api.com and requires an internet connection
to use. It offers a free API, with terms described on their site. Please refer
to the service's website for an authoritative source on API specifications.
This documentation summarizes a point in time understanding of the data source
though since it is a third party service, it may change in a manner that breaks
this tool or causes this documentation to become inaccurate. In no way is
inclusion of a data source in libchickadee an endorsement of the data source.

**Data source documentation:** https://ip-api.com/docs

Endpoints
^^^^^^^^^

The API supports a number of formats, though this resolver implementation
leverages the JSON APIs. This includes both the ``single`` and ``batch`` APIs
depending on the number of IP addresses requested for resolution.

* ``http://ip-api.com/json/{query}``
* ``http://ip-api.com/batch``

Fields
^^^^^^

These fields are in no particular order.

* status
* message
* continent
* continentCode
* country
* countryCode
* region
* regionName
* city
* district
* zip
* lat
* lon
* timezone
* currency
* isp
* org
* as
* asname
* mobile
* proxy
* hosting
* query

Limitations
^^^^^^^^^^^

This service has a free tier for non-commercial use, and is rate limited to
15 requests per minute. The returned HTTP header ``X-Rl`` contains the number
of requests remaining in the current rate limit window. ``X-Ttl`` contains the
seconds until the limit is reset.

The professional service is supported by chickadee and allows the execution
of unlimited requests, commercial use, and https endpoints. More details are
available on the data source website.

Module Documentation
--------------------

"""
import logging
import time
from datetime import datetime, timedelta

import requests
from tqdm import trange

from . import ResolverBase

logger = logging.getLogger(__name__)

__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

FIELDS = [  # Ordered list of fields to gather
    'query', 'count',
    'as', 'org', 'isp',
    'continent', 'country', 'regionName', 'city',
    'district', 'zip',
    'mobile', 'proxy', 'reverse',
    'lat', 'lon', 'timezone',
    'status', 'message'
]


class Resolver(ResolverBase):
    """Class to handle ip-api.com API queries for IP addresses.

    Sets endpoint to free API, confirms support for requested language,
    configures rate limit sleep timers.

    Args:
        fields (list): Collection of fields to request in resolution.
        lang (str): Language for returned results.
    """
    def __init__(self, fields=None, lang='en'):
        self.supported_langs = [
            'en', 'de', 'es', 'pt-BR', 'fr', 'ja', 'zh-CN', 'ru'
        ]
        super().__init__()

        self.lang = 'en' if lang not in self.supported_langs else lang
        self.fields = [] if not fields else fields
        self.uri = 'http://ip-api.com/'
        self.api_key = None
        self.enable_sleep = True
        self.wait_time = datetime.now()

    def rate_limit(self, headers):
        """Method to check rate limiting. Checks ``X-Rl`` and ``X-Ttl`` headers.

        Will set timer for rate limiting if ``X-Rl`` is less than 1 for
        duration of ``X-Ttl`` + 1 second.

        Args:
            headers (dict, CaseInsensitiveDict): Request header information.

        Return:
            None
        """
        if int(headers.get('X-Rl', '0')) < 1:
            self.wait_time = datetime.now() + \
                timedelta(seconds=int(headers.get('X-Ttl', '0'))+0.25)

    def sleeper(self):
        """Method to sleep operations for rate limiting. Executes sleep.

        Return:
            None
        """
        while True:
            now = datetime.now()
            wait_time = self.wait_time - now
            if wait_time.total_seconds() < 0:
                self.wait_time = datetime.now()
                return
            wt_sec = wait_time.total_seconds()+1  # add a buffer
            logger.info(
                'Sleeping for {} seconds due to rate limiting.'.format(wt_sec))
            time.sleep(wt_sec)

    def batch(self):
        """Handle batch query operations.

        Generally not called directly, should be called by ``self.query()`` to
        allow for the logic to handle which endpoint is preferred.

        Returns:
            (list): List of resolved IP address records with specified fields.
        """
        records = []
        for ip in self.data:
            records.append({'query': ip})

        resolved_recs = []
        if self.pbar:
            orig_recs = trange(0, len(records), 100,
                               desc="Resolving IPs", unit_scale=True)
        else:
            orig_recs = range(0, len(records), 100)

        for x in orig_recs:
            params = {
                'fields': ','.join(self.fields) if isinstance(self.fields, list) else self.fields,
                'lang': self.lang,
            }
            if self.api_key:
                params['key'] = self.api_key

            if self.enable_sleep:
                self.sleeper()

            rdata = requests.post(
                self.uri+"batch",
                json=records[x:x+100],
                params=params
            )

            if rdata.status_code == 200:
                self.rate_limit(rdata.headers)
                result_list = [x for x in rdata.json()]
                resolved_recs += result_list
            elif rdata.status_code == 429:
                self.rate_limit(rdata.headers)
                self.sleeper()
                return self.batch()
            else:  # pragma: no cover
                msg = "Unknown error encountered: {}".format(rdata.status_code)
                logger.error(msg)
                result_list = [{'query': result, 'status': 'failed', 'message': msg} for result in records[x:x+100]]
                resolved_recs += result_list
        return resolved_recs

    def single(self):
        """Handle single item query operations.

        Generally not called directly, should be called by ``self.query()`` to
        allow for the logic to handle which endpoint is preferred.

        Returns:
            (list): List of resolved IP address records with specified fields.
        """
        params = {
            'fields': ','.join(self.fields),
            'lang': self.lang,
        }
        if self.api_key:
            params['key'] = self.api_key

        if self.enable_sleep:
            self.sleeper()

        rdata = requests.get(
            self.uri+"json/"+self.data,
            params=params
        )
        if rdata.status_code == 200:
            self.rate_limit(rdata.headers)
            return [rdata.json()]
        if rdata.status_code == 429:
            self.rate_limit(rdata.headers)
            self.sleeper()
            return self.single()
        else:  # pragma: no cover
            msg = "Unknown error encountered: {}".format(rdata.status_code)
            logger.error(msg)
            return [{'query': self.data, 'status': 'failed', 'message': msg}]


class ProResolver(Resolver):
    """GeoIP resolver using the ip-api.com paid subscription.

    Sets endpoint to paid API, confirms support for requested language,
    and disables sleep functionality.

    Args:
        api_key (str): IP-API.com paid API key for requests.
        fields (list): Collection of fields to request in resolution.
        lang (str): Language for returned results.
    """
    def __init__(self, api_key, fields=None, lang='en'):  # pragma: no cover
        super().__init__()
        self.lang = 'en' if lang not in self.supported_langs else lang
        self.fields = [] if not fields else fields
        self.uri = 'https://pro.ip-api.com/'
        self.api_key = api_key
        self.enable_sleep = False
        logger.info("API key found.")
