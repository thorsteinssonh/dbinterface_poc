# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

@auth.requires_login()
def index():
    db.testdata.created_on.default = request.now
    db.testdata.created_on.writable=False
    #db.testdata.created_on.readable=False
    form = SQLFORM(db.testdata).process()
    if form.accepted:
        response.flash = "Success: Posted new data"
    allData = db(db.testdata).select(orderby=db.testdata.hospital.upper())
    return locals()

def show():
    entry = db.testdata( request.args(0,cast=int) )
    db.testdata_comments.testdata.default = entry.id
    db.testdata_comments.testdata.readable = False
    db.testdata_comments.testdata.writable = False
    form = SQLFORM(db.testdata_comments).process()
    comments = db(db.testdata_comments.testdata == entry.id).select()
    return locals()

@auth.requires_membership("managers")
def manage():
    grid = SQLFORM.grid(db.testdata)
    return locals()

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
    return service()
