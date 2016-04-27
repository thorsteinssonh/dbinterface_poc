# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

# Pages

def insert():
    form = SQLFORM(db.medical_device).process()
    if form.accepted:
        response.flash = "success"
    return locals()

def lookup():
    entries = db(db.medical_device).select()
    return locals()

def manage():
    grid = SQLFORM.grid(db.medical_device)
    return locals()

# RPC services
import xmlrpclib, datetime

@service.xmlrpc
def rpc_insert(data):
    unmarshal(data)
    db.device_history.insert(**data)

def unmarshal(data):
    """ perform any uncompleted data conversions for DAL.
        E.g. xmlrpclib communications leave unconverted datetime."""
    for key in data:
        if isinstance(data[key], xmlrpclib.DateTime):
            data[key] = datetime.datetime.strptime(data[key].value, "%Y%m%dT%H:%M:%S")

@service.xmlrpc
def rpc_remove(k):
    db.device_history(k).delete_record()

@service.xmlrpc
def rpc_drop():
    db.device_history.drop()

@service.xmlrpc
def rpc_get(k):
    record = db.device_history(k)
    if record:
        return record.as_dict()
    else:
        return None

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
