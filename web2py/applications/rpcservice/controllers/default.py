# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

#from gluon.tools import Service
#service = Service()

@service.xmlrpc
def get_entry(id):
    entry = db(db.testdata.id == id).select().first()
    if entry is None:
        return None
    else:
        return entry.as_dict()

@service.xmlrpc
def push_entry( entry ):
    db.testdata.created_on.default = request.now
    db.testdata.insert( **entry )
    return True

@service.xmlrpc
def push_anything(data_in):
    print data_in

@service.xmlrpc
def push_datetime(dt):
    print dt

#@auth.requires_membership("managers")
def manage():
    grid = SQLFORM.grid(db.testdata)
    return locals()

def insert():
    db.testdata.created_on.default = request.now
    db.testdata.created_on.writable=False
    #db.testdata.created_on.readable=False
    form = SQLFORM(db.testdata).process()
    if form.accepted:
        response.flash = "Success: Posted new data"
    return locals()


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
