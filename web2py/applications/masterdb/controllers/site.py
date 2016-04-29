# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

# Pages
@auth.requires_membership('manager')
def register():
    form = SQLFORM(db.site).process()
    if form.accepted:
        response.flash = "success"
    return locals()

@auth.requires_membership('observer')
def look_up():
    db.site.id.readable = False
    isMgr = auth.has_membership('manager')
    grid = SQLFORM.grid(db.site,
                        deletable=isMgr,
                        editable=isMgr,
                        create=isMgr)
    return locals()

@auth.requires_membership('observer')
def status():
    entries = db(db.site).select()
    return locals()
