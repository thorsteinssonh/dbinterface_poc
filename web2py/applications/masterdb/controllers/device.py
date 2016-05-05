# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
from applications.masterdb.modules.language_session import LanguageSession
from applications.masterdb.modules.exporters import MDBExporterPDF

class DevicePDF(MDBExporterPDF):
    title = T("Medical Device Transcript")
    search_keywords = request.vars.keywords
    row_key_styles = [{'key':'make',
                       'fmt':lambda x: x,
                       'wf':0.2},
                      {'key':'model',
                       'fmt':lambda x: x,
                       'wf':0.4},
                      {'key':'serial_no',
                       'fmt':lambda x: x,
                       'wf':0.2},
                      {'key':'device_type',
                       'wf':0.2}]
# Pages

@auth.requires_membership('manager')
@LanguageSession
def register():
    form = SQLFORM(db.device).process()
    if form.accepted:
        response.flash = "success"
    return locals()

@auth.requires_membership('observer')
@LanguageSession
def look_up():
    db.device.id.readable = False
    isMgr = auth.has_membership('manager')
    request.vars._export_filename = "device_transcript"
    grid = SQLFORM.grid(db.device,
                        deletable=isMgr,
                        editable=isMgr,
                        create=isMgr,
                        exportclasses={'pdf':(DevicePDF,'PDF')})
    return locals()

@auth.requires_membership('observer')
@LanguageSession
def status():
    max_hours = 1.0 # maximum time from last heartbeat (if too long indicate red in view)
    entries = db().select(db.device.ALL,
                          db.device_heartbeat.at_time,
                          db.device_heartbeat.site,
                          left=db.device_heartbeat.on(db.device.id==db.device_heartbeat.device),
                          groupby=db.device.id  )
    #entries = db(db.device).select()
    return locals()
