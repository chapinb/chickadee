# Chickadee

Yet another GeoIP resolution tool.

```
         _          _
        ('<        >')
       \(_)________( \
        (___________)\\        _____ _     _      _             _
           (     )     \      / ____| |   (_)    | |           | |
            |   |            | |    | |__  _  ___| | ____ _  __| | ___  ___
            |   |            | |    | '_ \| |/ __| |/ / _` |/ _` |/ _ \/ _ \
            |   |            | |____| | | | | (__|   < (_| | (_| |  __/  __/
           _|   |_            \_____|_| |_|_|\___|_|\_\__,_|\__,_|\___|\___|
          (_______)
```

Supported GeoIP back-ends:
* http://ip-api.com/ - Free to query up to 150 requests per minute. Unlimited
  API keys available for purchase.

## Installation

Currently you must use the source code (pip package coming soon).

### macOS and Linux

Requirements:
* Python 3.6+, installed on your path
* Virtualenv (`pip3 install virtualenv`)

1. Clone the git repo: `git clone https://github.com/chapinb/chickadee.git`
2. Create your virtual environment `virtualenv -p python3 venv3` and activate it (`source venv3/bin/activate`)
3. Install dependencies: `pip install -r requirements.txt`
4. `cd` into the `src` directory and run `python chickadee.py --help` to get started.

### Windows

Requirements:
* Python 3.6+, installed on your path
* Virtualenv (`pip.exe install virtualenv`)

1. Clone the git repo: `git clone https://github.com/chapinb/chickadee.git`
2. Create your virtual environment `virtualenv -p python3 venv3` and activate it (`source venv3/bin/activate`)
3. Install dependencies: `pip install -r requirements.txt`
4. `cd` into the `src` directory and run `python chickadee.py --help` to get started.

## Usage

The below shows the help information for using Chickadee. It can accept any of
the below formats:

* Loose IP addresses (either a single IP or a comma separated list)
* IPv4 or IPv6
* A path to a plaintext file containing IP addresses (even if they are among
  other data)
* A path to a gzip'd plaintext file (not an archive of multiple plaintext files)
* A path to a folder containing plaintext or gzip'd plaintext data

```
$ python chickadee.py --help
usage: chickadee.py [-h] [-f F] [-t {json,jsonl,csv}] [-w W] data

Sample Argparse

positional arguments:
  data                 Either an IP address, comma delimited list of IP
                       addresses, or path to a file or folder containing files
                       to check for IP address values. Currently supported
                       file types: plain text (ie logs, csv, json), gzipped
                       plain text

optional arguments:
  -h, --help           show this help message and exit
  -f F                 Fields to query (default: ['query', 'as', 'org',
                       'ispcontinent', 'country', 'regionName', 'city',
                       'district', 'zip', 'mobile', 'proxy', 'reverse', 'lat',
                       'lon', 'timezonestatus', 'message'])
  -t {json,jsonl,csv}  Output format (default: jsonl)
  -w W                 Path to file to write output (default:
                       <_io.TextIOWrapper name='<stdout>' mode='w'
                       encoding='UTF-8'>)

Built by Chapin Bryce, v.20190824
```

## Example

To resolve `8.8.8.8` and `1.1.1.1`. *The `jq` tool isn't a requirement, but is
a great utility for formatting and querying any JSON data.*

```
$ python chickadee.py 8.8.8.8,1.1.1.1 | jq '.'
{
  "as": "AS15169 Google LLC",
  "city": "Ashburn",
  "country": "United States",
  "district": "",
  "lat": 39.0438,
  "lon": -77.4874,
  "mobile": false,
  "org": "Google Inc.",
  "proxy": false,
  "query": "8.8.8.8",
  "regionName": "Virginia",
  "zip": "20149"
}
{
  "as": "AS13335 Cloudflare, Inc.",
  "city": "Sydney",
  "country": "Australia",
  "district": "",
  "lat": -33.8688,
  "lon": 151.209,
  "mobile": false,
  "org": "",
  "proxy": false,
  "query": "1.1.1.1",
  "regionName": "New South Wales",
  "zip": "1001"
}
```

Example of using the custom fields. Available field names can be found at: http://ip-api.com/docs/api:json

```
$ python chickadee.py 8.8.8.8,1.1.1.1 -t jsonl -f as,proxy
{"as": "AS15169 Google LLC", "proxy": false}
{"as": "AS13335 Cloudflare, Inc.", "proxy": false}
```

## Contributing

Please create a fork of the repository, make your changes, and submit a pull
request for review!

You can always use the issues tab to suggest features and identify bugs.
