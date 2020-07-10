# Changelog

## [Unreleased]

### Added

List of new features

* Added support to extract IP addresses from Windows Event logs (evtx files.)

### Fixed

Bugs addressed:

* [Issue-54](https://github.com/chapinb/chickadee/issues/54) - Fixed bug where an inconsistent data type was returned
  by the resolver.

### Changed

Modifications to existing functionality

* Increased unit test coverage. Leverage mocking for API requests.
* Improved code per Deepsource, PyCharm, and Sourcery recommendations.

### Removed

Features removed

## 20200407.2

This release includes:

* Features
  * BOGON IP Address filtering. Defaults to excluding BOGON IPs from resolution
* Bugs/Fixes
  * Adjusted argparse logic to ensure proper handling of `data` inputs
  * Added parameters to pass along the `api-key` configuration item
* Additional documentation, hosted at https://chapinb.com/chickadee
* Unit tests for reporting
* Refactored argument and update handling
* Moved common parser logic to init file


## 20191014

This release includes:

* Improved API request limit handling
* Support for Pro API keys for ip-api.com
* Improved logging
* Tests for chickadee script

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
