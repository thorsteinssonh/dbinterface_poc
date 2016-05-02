# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
from applications.masterdb.modules.language_session import LanguageSession

# Pages
@auth.requires_membership('manager')
@LanguageSession
def register():
    form = SQLFORM(db.site).process()
    if form.accepted:
        response.flash = "success"
    return locals()

@auth.requires_membership('observer')
@LanguageSession
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
    sites = db(db.site).select()
    # also collect info about devices at this site (last known address)
    last_hb = db().select(db.device_heartbeat.device,
                          db.device_heartbeat.site,
                          db.device_heartbeat.at_time,
                          groupby=db.device_heartbeat.device)
    for hb in last_hb:
        s = sites.find(lambda row: row.id == hb.site).first()
        if hasattr(s, 'device_list'):
            s.device_list.append(hb.device)
        else:
            s.device_list = [hb.device]
    return locals()
