#!/usr/bin/env bash
fgrep -Ri pdb libchickadee/**/*.py
pylint libchickadee
coverage run tests.py && coverage html
open htmlcov/index.html