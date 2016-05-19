#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
from datetime import datetime, time, date


BulletinContentType = ('device history summary','device status summary')

def bulletin_schedule_process():
    # run through bulletin definiations
    # and evaluate if triggered on this run
    now = datetime.utcnow()
    logfile="bulletin.log"
    f = open(logfile,'a')
    f.write("Starting "+str(now)+"\n")
    f.close()
    db = current.db
    rows = db(db.bulletin).select()
    for r in rows:
        if r.is_active:
            if r.last_execution:
                # allow 5min dead-time since last exec
                if (now - r.last_execution).total_seconds()/60.0 < 5.0:
                    f = open(logfile,'a')
                    f.write("dead-time... continue\n")
                    f.close()
                    continue
            if process_trigger(r.trigger_expression, now):
                f = open(logfile,'a')
                f.write("passed process trigger test...\n")
                f.close()
                # then execute bulletin task
                # create message
                message = create_bulletin_message( r.content_type, db, html=True )
                # send message
                send_bulletin(r.to_user, r.content_type, message)
                # update last_exectuion field
                db(db.bulletin.id == r.id).update(last_execution=now)
                db.commit() # commit required in modules
                ## debug signal
                f = open(logfile,'a')
                f.write("sent message\n")
                f.close()

weekday={'monday':0,
          'tuesday':1,
          'wednesday':2,
          'thursday':3,
          'friday':4,
          'saturday':5,
          'sunday':6} #Note: datetime numbering

def parse_trigger_expr(expr):
    """Expression can be in the form: 'time=HH:MM date=YYYY-MM-DD date=MM-DD weekday=monday ...' Returns a dict of results"""
    p = {'time':None,
         'date':None,
         'weekday':None}
    splt = expr.split()
    for statement in splt:
        key, val = statement.split("=")
        if key == 'time':
            H,M=val.split(":")
            h,m=int(H),int(M)
            if h>23 or h<0 or m>59 or m<0:
                raise ValueError('time values not in range')
            p[key]=(int(H),int(M))
        elif key == 'date':
            ds = val.split("-")
            if len(ds) == 3:
                p[key]=(int(ds[0]),int(ds[1]),int(ds[2]))
            elif len(ds) == 2:
                p[key]=(int(ds[0]),int(ds[1]))
            else:
                raise ValueError('invalid date expression, use YYYY-mm-dd or mm-dd')
        elif key == 'weekday':
            if val.lower() in weekday:
                p[key]=weekday[val.lower()]
            else:
                raise ValueError('unknown weekday, use Monday, Tuesday, ... Sunday')
    return p

class IS_TRIGGER_EXPR(object):
    """Custom validator for trigger expression field in db table"""
    def __init__(self, error_message='must be valid trigger expression'):
        self.error_message = error_message
    def __call__(self, value):
        try:
            parse_trigger_expr( value )
            return (value, None)
        except Exception as e:
            return (value, self.error_message+" - "+str(e))

def process_trigger(expr, dt):
    """ evaluates if expression, expr triggers given the datetime dt.
    Expression can be in the form: 'time=HH:MM date=YYYY-MM-DD date=MM-DD weekday=monday ...'"""
    p = parse_trigger_expr(expr)
    if (p['time'] is None) and (p['date'] is None) and (p['weekday'] is None):
        return False
    if p['time']:
        if not (dt.hour,dt.minute) == p['time']:
            return False
    if p['date']:
        if len(p['date']) == 2:
            if not (dt.month,dt.day) == p['date']:
                return False
        else:
            if not (dt.year,dt.month,dt.day) == p['date']:
                return False
    if p['weekday']:
        if not dt.weekday() == p['weekday']:
            return False
    return True


def markmin2html(text):
    # Note: for html emails, cannot reliably use <style> section in header
    # Instead use only minimal inline style attributes
    xml = MARKMIN(text).xml()
    xml = xml.replace('<table', '<table style="border-collapse: collapse;"')
    xml = xml.replace('<tr class="first"', '<tr style="border-bottom: 3px solid black;"')
    xml = xml.replace('<tr class="even"', '<tr style="background-color: #eee;"')
    xml = xml.replace('<td', '<td style="min-width:150px;"')
    return '<html><head></head><body>'+xml+'</body></html>'


def send_bulletin(user,subject,content):
    return current.mail.send(user.email,
                             subject,
                             content)

def test_bulletin_schedule(id, db):
    s = db(db.bulletin.id == id).select().first()
    # create message
    message = create_bulletin_message( s.content_type, db, html=True )
    # send message
    return send_bulletin(s.to_user, s.content_type, message)

def create_bulletin_message( type, db, html=True):
    if type in BulletinContentType:
        if type == "device status summary":
            # fetch current device info
            rows = db().select(db.device.ALL,
                                  db.device_heartbeat.at_time,
                                  db.device_heartbeat.site,
                                  left = db.device_heartbeat.on( db.device.id==db.device_heartbeat.device ),
                                  groupby=db.device.id  )
            # create message string
            bulletin = '#'+type.upper()+'\n##Generated at ' + datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC") + "\n"
            bulletin += "### ''Medical devices with following status:''\n"
            bulletin += "------------\n"
            bulletin += "**device** | **serial no** | **type** | **site** | **status** \n"
            now = datetime.utcnow()
            for r in rows:
                if r.device_heartbeat.at_time:
                    hbhours = (now - r.device_heartbeat.at_time).total_seconds()/3600.0
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
            if html:
                return markmin2html( bulletin )
            else:
                return bulletin
        elif type == "device history summary":
            return "Message not implemented yet"
