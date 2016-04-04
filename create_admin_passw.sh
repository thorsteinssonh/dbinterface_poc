#! /bin/bash
cd web2py
python -c "from gluon.widget import console; console();"
python -c "from gluon.main import save_password; save_password(raw_input('admin password: '),443)"
