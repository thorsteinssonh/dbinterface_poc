# -*- coding: utf-8 -*-

from language_session import LanguageSession
from gluon.tools import geocode

# Pages
@auth.requires_membership('manager')
@LanguageSession
def register():
    db.site.latitude.writable = False
    db.site.latitude.readable = False
    db.site.longitude.writable = False
    db.site.longitude.readable = False
    form = SQLFORM(db.site).process(onvalidation=process_geolocation)
    if form.accepted:
        response.flash = "success"
    return locals()

def process_geolocation(form):
    if form.vars.latitude is None and form.vars.address is not None:
        form.vars.latitude, form.vars.longitude = geocode(form.vars.address)

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
    # include map data
    mapdata = sites
    return locals()
