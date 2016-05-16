# -*- coding: utf-8 -*-
from applications.devicedb.modules.countries import Countries
from applications.devicedb.modules.device_types import DeviceTypes

# treatement centre table
db.define_table('site',
                Field('name', label=T("Name"), requires=IS_NOT_EMPTY()),
                Field('country', 'string', label=T("Country"),
                      requires=IS_IN_SET( Countries ),
                      represent = lambda name, row: T(name)),
                Field('address', label=T("Address")),
                Field('phone_number',
                       label=T("Phone Number"),
                       requires=IS_MATCH('^[+]?[\d]*[\s\d]*$',
                                         error_message='can only use +, spaces and digits')),
                format='%(name)s')

# medical device table
db.define_table('device',
                Field('device_type', 'string', label=T('Device Type'), requires=IS_IN_SET( DeviceTypes ),
                       represent = lambda name, row: T(name)),
                Field('make', 'string', label=T('Make')),
                Field('model', 'string', label=T('Model')),
                Field('serial_no', 'string',label=T('Serial No')),
                Field('special_alias', 'string',label=T('Alias')),
                format='%(make)s/%(model)s (%(special_alias)s)')

# medical device heartbeat (i.e. connectivity to masterdb)
db.define_table('device_heartbeat',
                Field('at_time', 'datetime', label=T('At Time'), required=True),
                Field('device', 'reference device',
                      label=T('Device'), required=True,
                      requires=IS_IN_DB(db, 'device.id', '%(make)s/%(model)s (%(special_alias)s)')),
                Field('site', 'reference site', 
                      label=T('Site'), required=True, 
                      requires=IS_IN_DB(db, 'site.id', '%(name)s')),
                Field('ip_address', 'string', label=T('IP Address')) )

# device history table
db.define_table('device_history',
                 Field('device', 'reference device', label=T('Device'), required=True, requires=IS_IN_DB(db,'device.id','%(make)s/%(model)s (%(special_alias)s)')),
                 Field('site', 'reference site', label=T('Site'), required=True, requires=IS_IN_DB(db,'site.id','%(name)s')),
                 Field('time_used', 'datetime', label=T('Used At')),
                 Field('time_received', 'datetime', label=T('Received At')),
                 Field('patient_id', 'integer', label=T('Patient Id')))
