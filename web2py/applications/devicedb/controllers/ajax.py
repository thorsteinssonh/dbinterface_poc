# -*- coding: utf-8 -*-
# try something like
from datetime import datetime

def dh_page_reload():
    return page_reload("device_history")

def page_reload(table_name):
    tbl_state = get_table_state(table_name)
    if session.dh_state:
        if session.dh_state >= tbl_state:
            # i.e. if less or equal amount data, do nothing
            session.dh_state = tbl_state
            return False
        else:
            # if more data signal a reload
            session.dh_state = tbl_state
            session.flash = T("new data")
            return True
    else:
            session.dh_state = tbl_state
    return False

def get_table_state(table_name):
    return db(db[table_name]).count()

def test():
    rows = db(db.device_history).select()
    return locals()
