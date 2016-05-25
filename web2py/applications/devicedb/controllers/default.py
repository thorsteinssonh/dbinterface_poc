# -*- coding: utf-8 -*-

from language_session import LanguageSession
from datetime import datetime, timedelta

@LanguageSession
def index():
    # fetch 5 latest device events to decorate front page
    latest_history = db(db.device_history).select(orderby=~db.device_history.time_used,
                                                  limitby=(0,5))
    if len(latest_history)==0:
        del latest_history
    # hide location of devices and user id if member is not observer or logged in
    # Note: this is a bit quick and dirty
    #       access controll more secure with model fields properties
    if not auth.has_membership('observer'):
        for x in latest_history:
            x.patient_id = T("restricted")
            x.site.name = T("restricted")
            x.site.country = T("restricted")
    
    # introduction
    title = T('CHC Healthcare Group')
    subtitle = T('medical device database')
    introductory_text = T('The CHCDeviceDB collects information about medical devices provisioned by the CHC Healthcare Group in Taiwan. If you need access to the data here within you must register and ask an administrator for privileges to access the data.')
    # service summary
    service_summary={}
    service_summary['total_sites'] = db(db.site).count()
    service_summary['total_devices'] = db(db.device).count()
    service_summary['total_treatments'] = db(db.device_history.time_used < request.now).count()
    service_summary['total_patients'] = len(db(db.device_history.time_used < request.now).select(db.device_history.site, db.device_history.patient_id, distinct=True))
    # set page reload trigger (for ajax included in view)
    page_reload = "/ajax/dh_page_reload"
    # include map data
    mapdata = db(db.site).select()
    if auth.has_membership('observer'):
        for h in latest_history:
            s = mapdata.find(lambda row: row.id == h.site).first()
            if s is not None:
                if not hasattr(s,'latest_event'):
                    s.latest_event = event_str(h)
    return locals()

def event_str(h):
    dtstr = ""
    dtstr += "{0}/{1} ".format(h.device.make, h.device.model)
    if h.use_type is not None:
        dtstr += h.use_type+" "
    if h.time_used is not None:
        dt = (request.utcnow - h.time_used).total_seconds()/60.0
        if dt < 60.0:
            dtstr += "%.1f "%(dt) + T("minutes ago")
        elif dt < 1440.0:
            dtstr += "%.1f "%(dt/60.0) + T("hours ago")
        else:
            dtstr += "%.1f "%(dt/1440.0) + T("days ago")
    return dtstr

@LanguageSession
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
