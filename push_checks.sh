#!/usr/bin/env bash
fgrep -Ri pdb libchickadee/**/*.py
flake8 libchickadee --count --show-source --statistics
coverage run tests.py && coverage html
open htmlcov/index.html