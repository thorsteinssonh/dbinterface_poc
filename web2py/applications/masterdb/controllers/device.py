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
    form = SQLFORM(db.device).process()
    if form.accepted:
        response.flash = "success"
    return locals()

@auth.requires_membership('observer')
def look_up():
    db.device.id.readable = False
    isMgr = auth.has_membership('manager')
    grid = SQLFORM.grid(db.device,
                        deletable=isMgr,
                        editable=isMgr,
                        create=isMgr)
    return locals()

@auth.requires_membership('observer')
def status():
    max_hours = 1.0 # maximum time from last heartbeat (if too long indicate red in view)
    entries = db().select(db.device.ALL,
                          db.device_heartbeat.at_time,
                          db.device_heartbeat.site,
                          left=db.device_heartbeat.on(db.device.id==db.device_heartbeat.device),
                          groupby=db.device.id  )
    #entries = db(db.device).select()
    return locals()
