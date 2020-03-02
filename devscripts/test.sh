#!/usr/bin/env bash
cd ..
flake8 libchickadee --count --show-source --statistics
coverage run -m unittest discover
coverage xml
coverage report
cd doc_src
make html
cd ../devscripts
