# -*- coding: utf-8 -*-

LanguageSession = local_import('language_session').LanguageSession
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
            success = test_bulletin_schedule(request.args[1])
            if success: session.flash = "message sent"
            else: session.flash = "sending failed"
            redirect(URL('bulletin_schedules'))
    # continue to display page
    db.bulletin.is_active.readable = False
    db.bulletin.is_active.writable = False
    form = SQLFORM(db.bulletin).process()
    if form.accepted:
        response.flash = "success"
    schedules = db(db.bulletin).select()
    return locals()

@auth.requires_membership('manager')
def testmarkmin():
    return markmin2html(create_bulletin_message('device status summary'))

def markmin2html(text):
    xml = MARKMIN(text).xml()
    return '<html><head><style>.first td{border-bottom: 3px solid black;} .table {border-collapse: collapse; overflow:scroll;}</style></head><body>'+xml+'</body></html>'

@auth.requires_membership('manager')
def test_bulletin_schedule(id):
    s = db(db.bulletin.id == id).select().first()
    # create message
    message = markmin2html( create_bulletin_message( s.content_type ) )
    # send message
    return send_bulletin(s.to_user, s.content_type, message)

def create_bulletin_message( type ):
    if type in BulletinContentType:
        if type == "device status summary":
            # fetch current device info
            rows = db().select(db.device.ALL,
                                  db.device_heartbeat.at_time,
                                  db.device_heartbeat.site,
                                  left = db.device_heartbeat.on( db.device.id==db.device_heartbeat.device ),
                                  groupby=db.device.id  )
            # create message string
            bulletin = '#'+type.upper()+'\n##Generated at ' + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n"
            bulletin += "### ''Medical devices with following status:''\n"
            bulletin += "------------\n"
            bulletin += "**device** | **serial no** | **type** | **site** | **status** \n"
            for r in rows:
                if r.device_heartbeat.at_time:
                    hbhours = (request.now - r.device_heartbeat.at_time).total_seconds()/3600.0
                    if hbhours < 24.0:
                        status="normal"
                    else:
                        if hbhours > 48.0:
                            status="delay:%0.1fd"%(hbhours/24.0)
                        else:
                            status="delay:%0.1fh"%hbhours
                else:
                    hbhours = None
                    status="no signals"
                site = str(r.device_heartbeat.site.name) if r.device_heartbeat.site is not None else ""
                bulletin += "%s | %s | %s | %s | %s \n"%(r.device.make+"/"+r.device.model,
                                                            str(r.device.serial_no),
                                                            str(r.device.device_type),
                                                            site,
                                                            status)
            bulletin += "------------:table\n"
            return bulletin

def send_bulletin(user,subject,content):
    return mail.send(user.email,
                     subject,
                     content)

@auth.requires_membership('manager')
def toggle_bulletin_schedule(id):
    r = db(db.bulletin.id == id).select().first()
    if r.is_active:
        db(db.bulletin.id == id).update(is_active=False)
    else:
        db(db.bulletin.id == id).update(is_active=True)

@auth.requires_membership('manager')
def delete_bulletin_schedule(id):
    db(db.bulletin.id == id).delete()
