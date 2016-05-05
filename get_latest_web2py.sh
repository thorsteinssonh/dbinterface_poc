#! /bin/bash

# clean out previous version
find ./web2py/* -not -path "./web2py/routes.py" -not -path "./web2py/gluon/contrib/fpdf/font/*" -not -path "./web2py/applications/*" -not -path "./web2py/parameters_443.py" -delete

# get latest
wget http://www.web2py.com/examples/static/web2py_src.zip
unzip web2py_src.zip
rm web2py_src.zip
