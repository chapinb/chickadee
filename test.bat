flake8 libchickadee
coverage run -m unittest discover
coverage xml
coverage report
cd doc_src
make.bat html
cd ..
