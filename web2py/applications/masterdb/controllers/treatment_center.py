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
    form = SQLFORM(db.treatment_center).process()
    if form.accepted:
        response.flash = "success"
    return locals()

def lookup():
    entries = db(db.treatment_center).select()
    return locals()

def manage():
    grid = SQLFORM.grid(db.treatment_center)
    return locals()

# RPC services
import xmlrpclib, datetime

@service.xmlrpc
def rpc_insert(data):
    unmarshal(data)
    db.treatment_center.insert(**data)

def unmarshal(data):
    """ perform any uncompleted data conversions for DAL.
        E.g. xmlrpclib communications leave unconverted datetime."""
    for key in data:
        if isinstance(data[key], xmlrpclib.DateTime):
            data[key] = datetime.datetime.strptime(data[key].value, "%Y%m%dT%H:%M:%S")

@service.xmlrpc
def rpc_remove(k):
    db.treatment_center(k).delete_record()

@service.xmlrpc
def rpc_drop():
    db.treatment_center.drop()

@service.xmlrpc
def rpc_get(k):
    record = db.treatment_center(k)
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
