# Changelog

## 20190917

This release includes:

* Removed left over debugging statement

## 20190915

This release includes:

* Added XLSX support (by extension only)
* Error handling to continue when unsupported document is scanned, or encoding 
  error is encountered
* Added a CHANGELOG (*so meta*)
* Added logging
* Added unittesting

## 20190910

This release includes:

* Code refactoring and clean up
* Moving status messages to stderr to allow for ease of piping data

## 20190907.3

Updated script entry point for cross platform compatibility.

## 20190907

This release brings:

* Fixes for the default fields and removal of unnecessary dependencies.
* Restructured for pip packaging and to support additional parsers or geoip backends.
* Installed as a command line tool with pip, allowing for system wide usage once installed.
* Available at https://pypi.org/project/chickadee/

Please submit bugs, feature requests, and more to https://github.com/chapinb/chickadee

## 20190827

The initial release of Chickadee with support for:

* ip-api.com backend
* Resolving lists of IP addresses
* Extracting IP addresses from plain text (ie logs, json) and gzip'd files (not multi-file archives)
* Recursively extracting IP addresses from a folder of files (ie /var/log)
* Outputting the data to CSV, JSON, and JSON Lines (newline delimited array)
