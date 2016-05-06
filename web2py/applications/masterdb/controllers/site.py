# -*- coding: utf-8 -*-

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
    db.site.country.represent = lambda name, row: T(name)
    grid = SQLFORM.grid(db.site,
                        deletable=isMgr,
                        editable=isMgr,
                        create=isMgr)
    return locals()

@auth.requires_membership('observer')
@LanguageSession
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
