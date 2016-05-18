# -*- coding: utf-8 -*-

from language_session import LanguageSession
from datetime import datetime, timedelta

@LanguageSession
def index():
    if auth.has_membership('observer'):
        latest_history = db(db.device_history).select(orderby=~db.device_history.time_used,
                                                      limitby=(0,10))
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
    return locals()

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
