# Chickadee

Yet another GeoIP resolution tool.

![build status](https://travis-ci.org/chapinb/chickadee.svg?branch=master)

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

* http://ip-api.com/ - Free to query up to 45 requests per minute. Unlimited
  API keys available for purchase.

## Installation

You may install Chickadee on your platform using `pip install chickadee` (you
may need to use `pip3` depending on your system configuration).
**Please ensure you are using Python 3**

You may also install via the source code as detailed below.

### macOS and Linux

Requirements:

* Python 3+, installed on your path
* Virtualenv (`pip3 install virtualenv`)

1. Clone the git repo: `git clone https://github.com/chapinb/chickadee.git`
2. Create your virtual environment `virtualenv -p python3 venv3` and
   activate it (`source venv3/bin/activate`)
3. Install dependencies: `pip install .`
4. Run `chickadee --help` to get started.

### Windows

Requirements:

* Python 3+, installed on your path
* Virtualenv (`pip.exe install virtualenv`)

1. Clone the git repo: `git clone https://github.com/chapinb/chickadee.git`
2. Create your virtual environment `virtualenv -p python3 venv3` and activate
   it (`source venv3/Scripts/activate.bat`)
3. Install dependencies: `pip install .`
4. Run `chickadee --help` to get started.

## Usage

The below shows the help information for using Chickadee. It can accept any of
the below formats:

* Loose IP addresses (either a single IP or a comma separated list)
* IPv4 or IPv6
* A path to a plaintext file containing IP addresses (even if they are among
  other data)
* A path to a gzip'd plaintext file (not an archive of multiple plaintext files)
* A path to a folder containing plaintext or gzip'd plaintext data

```text
$ chickadee --help
usage: chickadee [-h] [-f FIELDS] [-t {json,jsonl,csv}] [-w FILENAME.JSON]
                 [-s] [--lang {en,de,es,pt-BR,fr,ja,zh-CN,ru}] [-p] [-v] [-V]
                 [-l LOG]
                 [data [data ...]]

Yet another GeoIP resolution tool.

Will use the free rate limited ip-api.com service for resolution.
Please set an environment variable named CHICKADEE_API_KEY with the
value of your API key to enabled unlimited requests with the
commercial API

positional arguments:
  data                  Either an IP address, comma delimited list of IP
                        addresses, or path to a file or folder containing files
                        to check for IP address values. Currently supported file
                        types: plain text (ie logs, csv, json), gzipped plain
                        text, xlsx (must be xlsx extension). Can accept plain
                        text data as stdin. (default: <_io.TextIOWrapper
                        name='<stdin>' mode='r' encoding='UTF-8'>)

optional arguments:
  -h, --help            show this help message and exit
  -f FIELDS, --fields FIELDS
                        Comma separated fields to query (default:
                        query,count,as,org,isp,continent,country,regionName,
                        city,district,zip,mobile,proxy,reverse,lat,lon,
                        timezone,status,message)
  -t {json,jsonl,csv}, --output-format {json,jsonl,csv}
                        Output format (default: jsonl)
  -w FILENAME.JSON, --output-file FILENAME.JSON
                        Path to file to write output (default:
                        <_io.TextIOWrapper name='<stdout>' mode='w'
                        encoding='UTF-8'>)
  -n, --no-resolve      Only extract IP addresses, don't resolve. (default: True)
  -s, --single          Use the significantly slower single item API. Adds
                        reverse DNS. (default: False)
  --lang {en,de,es,pt-BR,fr,ja,zh-CN,ru}
                        Language (default: en)
  -p, --progress        Enable progress bar (default: False)
  -v, --verbose         Include debug log messages (default: False)
  -V, --version         Displays version
  -l LOG, --log LOG     Path to log file (default: ./chickadee.log)

Built by Chapin Bryce, v.20191220
```

[![asciicast](https://asciinema.org/a/266509.png)](https://asciinema.org/a/266509)

## Example

To resolve `8.8.8.8` and `1.1.1.1`. *The `jq` tool isn't a requirement, but is
a great utility for formatting and querying any JSON data.*

```text
$ chickadee 8.8.8.8,1.1.1.1 | jq '.'
{
  "country": "United States",
  "regionName": "Virginia",
  "city": "Ashburn",
  "district": "",
  "zip": "20149",
  "lat": 39.0438,
  "lon": -77.4874,
  "org": "Google LLC",
  "as": "AS15169 Google LLC",
  "mobile": false,
  "proxy": false,
  "query": "8.8.8.8",
  "count": 1,
  "isp": null,
  "continent": null,
  "reverse": null,
  "timezone": null,
  "status": null,
  "message": null
}
{
  "country": "Australia",
  "regionName": "New South Wales",
  "city": "Sydney",
  "district": "",
  "zip": "1001",
  "lat": -33.8688,
  "lon": 151.209,
  "org": "",
  "as": "AS13335 Cloudflare, Inc.",
  "mobile": false,
  "proxy": false,
  "query": "1.1.1.1",
  "count": 1,
  "isp": null,
  "continent": null,
  "reverse": null,
  "timezone": null,
  "status": null,
  "message": null
}
```

Example of using the custom fields. Available field names are at: http://ip-api.com/docs/api:json

```text
$ chickadee 8.8.8.8,1.1.1.1 -t jsonl -f as,proxy
{"as": "AS15169 Google LLC", "proxy": false}
{"as": "AS13335 Cloudflare, Inc.", "proxy": false}
```

## Known bugs

Below are a list of known bugs. Please report any new bugs identified or
submit a PR to patch any of the below or ones you found on your own. No one
is perfect :)

* IPv6 addresses expressed in expanded form in the source document
  are not properly deduplicated against discovered IPv6 addresses in compressed
  form.
* While you can provide multiple input files in the same instance, the IPs will
  only be distinct to a single input item. For example, if you provide a file
  and folder as two inputs to the same invocation all IPs within a single
  file will be deduped, then separately all IPs within the files in the
  directory will be deduped. This means you may have duplicate resolutions in
  the same output in this case.
* JSON and CSV output will show column/field names even if a value is not
  present. Please enter an issue if this does not support your usecase.

## Contributing

Please create a fork of the repository, make your changes, and submit a pull
request for review!

You can always use the issues tab to suggest features and identify bugs.
