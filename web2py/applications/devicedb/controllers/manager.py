# -*- coding: utf-8 -*-

from language_session import LanguageSession
from bulletin import send_bulletin, create_bulletin_message, test_bulletin_schedule
from sqlite3 import OperationalError
from datetime import datetime


@auth.requires_membership('manager')
@LanguageSession
def sql():
    tables = db.tables()
    form = SQLFORM.factory(Field('query_name','string', required=False, notnull=True),
                           Field('sql_query','text', required=True, notnull=True,
                                 requires=IS_NOT_EMPTY(error_message="Please enter a query")),
                           submit_button=T('Run query'))
    form.element('textarea[name=sql_query]')['_style'] = 'height:120px;'
    form.vars.sql_query = """-- Enter SQL here, e.g.
select * from device"""
    if form.process(keepvalues=True).accepted:
        try:
            sql_result = db.executesql(form.vars.sql_query, as_dict=True)
        except (OperationalError,RuntimeError) as sql_error:
            response.flash = "sql query failed"
            sql_result = None
        else:
            sql_error = None
    else:
        sql_result = None
        sql_error = None
    return locals()

@auth.requires_membership('manager')
def bulletin():
    grid = SQLFORM.grid(db.bulletin)
    return locals()

@auth.requires_membership('manager')
def bulletin_schedules():
    # handle arguments
    if len(request.args)==2:
        if request.args[0]=="delete":
            delete_bulletin_schedule(request.args[1])
            redirect(URL('bulletin_schedules'))
        elif request.args[0]=="toggle":
            toggle_bulletin_schedule(request.args[1])
            redirect(URL('bulletin_schedules'))
        elif request.args[0]=="test":
            success = test_bulletin_schedule(request.args[1], db)
            if success: session.flash = "message sent"
            else: session.flash = "sending failed"
            redirect(URL('bulletin_schedules'))
    # continue to display page
    db.bulletin.is_active.readable = False
    db.bulletin.is_active.writable = False
    db.bulletin.last_execution.readable = False
    db.bulletin.last_execution.writable = False

    form = SQLFORM(db.bulletin).process()
    if form.accepted:
        response.flash = "success"
    schedules = db(db.bulletin).select()
    return locals()

@auth.requires_membership('manager')
def testmarkmin():
    return create_bulletin_message('device status summary', db, html=True)


def toggle_bulletin_schedule(id):
    r = db(db.bulletin.id == id).select().first()
    if r.is_active:
        db(db.bulletin.id == id).update(is_active=False)
    else:
        db(db.bulletin.id == id).update(is_active=True)


def delete_bulletin_schedule(id):
    db(db.bulletin.id == id).delete()

# Can unedit following if want to register scheduled process
#@auth.requires_membership('manager')
#def start_bs():
#    from bulletin import bulletin_schedule_process
#    scheduler.queue_task('bulletin_schedule_process',
#                         repeats=0,
#                         period=10)
#    return "done"
