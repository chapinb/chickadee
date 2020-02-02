#!/usr/bin/env bash
fgrep -Ri pdb libchickadee/**/*.py
flake8 libchickadee --count --show-source --statistics
coverage run -m unittest discover
coverage xml
coverage report