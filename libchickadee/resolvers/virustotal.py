"""
VirusTotal Resolver
===================

"""
import collections
import functools
import logging
import operator
import time
from datetime import datetime

import requests
from tqdm import tqdm

from . import ResolverBase

logger = logging.getLogger(__name__)

__author__ = 'Chapin Bryce'
__date__ = 20200302
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = 'Resolver for VirusTotal'

FIELDS = [
    'query', 'count',
    'asn', 'country',
    'subnet',
    'resolution_count', 'detected_sample_count', 'undetected_sample_count',
    'detected_url_count', 'undetected_url_count',
    'status', 'message'
]

NON_DEFAULT_FIELDS = [
    "resolutions", "detected_samples", "undetected_samples", "detected_urls", "undetected_urls"
]


class ProResolver(ResolverBase):
    def __init__(self, api_key, fields=None, lang="en"):

        super().__init__()

        self.supported_langs = [
            "en"
        ]
        self.lang = 'en' if lang not in self.supported_langs else lang
        self.fields = FIELDS if not fields else fields
        self.uri = "https://www.virustotal.com/vtapi/v2/ip-address/report"
        self.api_key = api_key
        self.enable_sleep = True
        self.wait_time = datetime.now()
        logger.info("API key found")

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

        # TODO return code 204 = rate limiting.
        #   You may have exceeded one of:
        #       * minute limit (wait till next minute)
        #       * daily limit (exit and warn)
        #       * monthly limit (exit and warn)
        #
        # x-api-message: You have reached your API quota
        # limits, please do not hesitate to contact us at
        # contact@virustotal.com in order to license more
        # quota or get access to advanced API calls.

    def batch(self):
        # Not supported
        all_ips = self.data
        records = []
        if self.pbar:
            all_ips = tqdm(self.data)
        for x in all_ips:
            self.data = x
            records.append(self.single())
        return self.single()

    def single(self):
        params = {
            'apikey': self.api_key,
            'ip': self.data
        }
        if self.enable_sleep:
            self.sleeper()

        rdata = requests.get(
            self.uri, params=params
        )

        if rdata.status_code == 200:
            return [self.parse_vt_resp(self.data, rdata.json())]
        if rdata.status_code == 204:
            # Rate limit
            self.sleeper()
        elif rdata.status_code == 400:
            logger.error("Incorrect request. Please check input data")
        elif rdata.status_code == 403:
            logger.error("Authorization error. Please check API key")
        else:
            # TODO error handling
            logger.error("Unknown error occurred, please report")

    def parse_vt_resp(self, query, vt_resp):
        attributes = dict.fromkeys(self.fields.copy())
        attributes.update({
            "query": query,
            "asn": "",
            "continent": vt_resp.get("continent"),
            "country": vt_resp.get("country"),
            "subnet": vt_resp.get("network"),
            "status": vt_resp.get("response_code"),
            "message": vt_resp.get("IP address in dataset"),
            "whois": "",
        })

        # ASNs
        if vt_resp.get("asn"):
            attributes["asn"] = "AS{} {}".format(
                vt_resp.get("asn"), vt_resp.get("as_owner")
            )

        # Parse WhoIS
        # OtherRemarks holds info not stored in key/value config
        whois = {"OtherRemarks": ""}
        for line in vt_resp.get('whois', "").split("\n"):
            if len(line) == 0:
                continue
            if ':' not in line:
                whois["OtherRemarks"] += line+"\n"
                continue
            split_line = line.split(":", 1)
            whois[split_line[0].strip()] = split_line[1].strip()
        attributes["whois"] = whois

        # Parse Resolutions
        attributes["resolution_count"] = len(vt_resp.get("resolutions", []))
        hostname_set = {x.get('hostname') for x in
                        vt_resp.get("resolutions", [])}
        attributes["resolutions"] = sorted(list(hostname_set))

        # Parse Detected Communicating, Download, and Referrer Samples
        # * Get count
        # * Get all hashes
        attributes["detected_sample_count"] = len(vt_resp.get("detected_communicating_samples", [])) + \
            len(vt_resp.get("detected_downloaded_samples", [])) + len(vt_resp.get("detected_referrer_samples", []))
        detected_communicating_samples = {
            x.get('sha256'): x.get('positives')
            for x in vt_resp.get('detected_communicating_samples', [])}
        detected_downloaded_samples = {
            x.get('sha256'): x.get('positives')
            for x in vt_resp.get('detected_downloaded_samples', [])}
        detected_referrer_samples = {
            x.get('sha256'): x.get('positives')
            for x in vt_resp.get('detected_referrer_samples', [])}

        # Sum up the counts across categories for the same samples
        attributes["detected_samples"] = dict(
            functools.reduce(
                operator.add, map(
                    collections.Counter, [detected_communicating_samples,
                                          detected_downloaded_samples,
                                          detected_referrer_samples])))

        # Parse Undetected Communicating Samples
        # * Get count
        # * Get all hashes
        attributes["undetected_sample_count"] = len(vt_resp.get("undetected_communicating_samples", [])) + \
            len(vt_resp.get("undetected_downloaded_samples", [])) + len(vt_resp.get("undetected_referrer_samples", []))
        undetected_samples = {
            x.get('sha256') for x in
            vt_resp.get('undetected_communicating_samples', [])}
        undetected_samples = undetected_samples.union({
            x.get('sha256') for x in
            vt_resp.get('undetected_downloaded_samples', [])})
        undetected_samples = undetected_samples.union({
            x.get('sha256') for x in
            vt_resp.get('undetected_referrer_samples', [])})
        attributes["undetected_samples"] = sorted(list(undetected_samples))

        # Parse Detected URLs
        # * Get count
        # * Get all defanged URLs
        attributes["detected_url_count"] = len(
            vt_resp.get("detected_urls", []))
        detected_urls = {
            self.defang_ioc(x.get('url')): x.get('positives')
            for x in vt_resp.get('detected_urls', [])}
        attributes["detected_urls"] = detected_urls

        # Parse Undetected URLs
        # * Get count
        # * Get all defanged URLs
        # The API does not expose this as a key/value object
        # but instead as a list where the elements are:
        # * 0: URL
        # * 1: SHA256 Hash value
        # * 2: Number of positive detections
        # * 3: Number of scanners
        # * 4: Time of last scan
        attributes["undetected_url_count"] = len(
            vt_resp.get("undetected_urls", []))
        detected_urls = {
            self.defang_ioc(x[0])
            for x in vt_resp.get('undetected_urls', [])}
        attributes["undetected_urls"] = sorted(list(detected_urls))

        return attributes
