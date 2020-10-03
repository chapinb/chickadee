# Chickadee

Yet another IP address enrichment tool.

```text
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

![build status](https://travis-ci.org/chapinb/chickadee.svg?branch=master)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/chapinb/chickadee.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/chapinb/chickadee/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/chapinb/chickadee.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/chapinb/chickadee/context:python)
![Unit Tests](https://github.com/chapinb/chickadee/workflows/Unit%20Tests/badge.svg)
![Docstring Coverage](.github/images/interrogate.svg)
[![Coverage Status](https://coveralls.io/repos/github/chapinb/chickadee/badge.svg)](https://coveralls.io/github/chapinb/chickadee)
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)
[![PyPI version](https://badge.fury.io/py/chickadee.svg)](https://badge.fury.io/py/chickadee)
[![PyPi downloads](https://pypip.in/d/chickadee/badge.png)](https://pypistats.org/packages/chickadee)
[![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/chapinb/chickadee/?ref=repository-badge)


Supported IP address resolvers:

* https://ip-api.com/ - Free to query up to 45 requests per minute. Unlimited
  API keys available for purchase.
* https://virustotal.com/ - API key needed to query. Rate limited to 4 requests per minute.

## Documentation

This project's documentation is available in the `docs/` folder,
or hosted on GitHub at [https://chapinb.com/chickadee/](https://chapinb.com/chickadee/).

Specific documentation:

* [Installation](https://chapinb.com/chickadee/index.html#installation)
* [Using chickadee](https://chapinb.com/chickadee/utilities.html#usage)
* [Examples](https://chapinb.com/chickadee/utilities.html#chickadee-examples)
* [Contributing](https://chapinb.com/chickadee/index.html#contribution)
* [Resolver documentation](https://chapinb.com/chickadee/resolvers.html)
* [File parser documentation](https://chapinb.com/chickadee/parsers.html)

## Known bugs

Below are a list of known bugs. Please report any new bugs identified or
submit a PR to patch any of the below or ones you found on your own. No one
is perfect :)

* IPv6 addresses expressed in expanded form in the source document
  are not properly deduplicated against discovered IPv6 addresses in compressed
  form.
* While you can provide multiple input files in the same instance, the IPs
  are distinct to a single input item. For example, if you provide a file
  and folder as two inputs to the same invocation, chickadee will dedupe
  all IPs within the single file, then separately dedupe all IPs within
  the files in the directory. This means you may have duplicate resolutions in
  the same output in this case.
* JSON and CSV output will show column/field names even if a value is not
  present. Please enter an issue if this does not support your usecase.

## Contributing

Please create a fork of the repository, make your changes, and submit a pull
request for review!

You can always use the issues tab to suggest features and identify bugs.
