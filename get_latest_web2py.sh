#! /bin/bash

# clean out previous version
find ./web2py/* -not -path "./web2py/applications/*" -delete

# get latest
wget http://www.web2py.com/examples/static/web2py_src.zip
unzip web2py_src.zip
rm web2py_src.zip
