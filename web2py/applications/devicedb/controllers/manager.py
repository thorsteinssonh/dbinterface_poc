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
    # check scheduler worker status
    scheduler_active = (request.now - sched_db(sched_db.scheduler_worker).select().first().last_heartbeat).total_seconds() < 120.0
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

from gluon.languages import (read_possible_languages, read_dict, write_dict,
                             read_plural_dict, write_plural_dict)
from gluon.admin import apath
from gluon.utils import md5_hash

@auth.requires_membership('manager')
@LanguageSession
def edit_language():
    """ Edit language file """
    #app = get_app()
    lang = ("zh-tw",T("Mandarin"))
    args = ['devicedb','languages',lang[0]+'.py']
    filename = '/'.join(args)
    response.title = args[-1]
    strings = read_dict(apath(filename, r=request))

    if '__corrupted__' in strings:
        form = SPAN(strings['__corrupted__'], _class='error')
        return dict(filename=filename, form=form)

    keys = sorted(strings.keys(), lambda x, y: cmp(
        unicode(x, 'utf-8').lower(), unicode(y, 'utf-8').lower()))
    rows = []
    rows.append(H2(T('Original/Translation')))

    for key in keys:
        name = md5_hash(key)
        s = strings[key]
        (prefix, sep, key) = key.partition('\x01')
        if sep:
            prefix = SPAN(prefix + ': ', _class='tm_ftag')
            k = key
        else:
            (k, prefix) = (prefix, '')

        _class = 'untranslated' if k == s else 'translated'

        if len(s) <= 40:
            elem = INPUT(_type='text', _name=name, value=s,
                         _size=70, _class=_class)
        else:
            elem = TEXTAREA(_name=name, value=s, _cols=70,
                            _rows=5, _class=_class)

        # Making the short circuit compatible with <= python2.4
        k = (s != k) and k or B(k)

        new_row = DIV( LABEL(prefix, k, _style="font-weight:normal;"),
                      CAT(elem, '\n', TAG.BUTTON(
                    T('delete'),
                    _onclick='return delkey("%s")' % name,
                    _class='btn' )), _id=name, _class='span6 well well-small')

        rows.append(DIV(new_row,_class="row-fluid"))
    rows.append(DIV(INPUT(_type='submit', _value=T('update'), _class="btn btn-primary"), _class='controls'))
    form = FORM(*rows)
    if form.accepts(request.vars, keepvalues=True):
        strs = dict()
        for key in keys:
            name = md5_hash(key)
            if form.vars[name] == chr(127):
                continue
            strs[key] = form.vars[name]
        write_dict(apath(filename, r=request), strs)
        session.flash = T('saved on UTC') + request.utcnow.strftime(" %Y-%m-%d %H:%M")
        redirect(URL(r=request, args=request.args))
    return dict(app=args[0], filename=filename, form=form, lang=lang)
