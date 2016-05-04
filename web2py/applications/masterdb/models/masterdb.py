# -*- coding: utf-8 -*-
from applications.masterdb.modules.countries import Countries
from applications.masterdb.modules.device_types import DeviceTypes

# treatement centre table
db.define_table('site',
                Field('name', label=T("Name"), requires=IS_NOT_EMPTY()),
                Field('country', 'string', label=T('Country'), requires=IS_IN_SET( Countries )),
                Field('address'),
                Field('phone_number', requires=IS_MATCH('^[+]?[\d]*[\s\d]*$', error_message='can only use +, spaces and digits')),
                format='%(name)s')

# medical device table
db.define_table('device',
                Field('device_type', 'string', requires=IS_IN_SET( DeviceTypes )),
                Field('make', 'string'),
                Field('model', 'string'),
                Field('serial_no', 'string'),
                format='%(make)s/%(model)s')

# medical device heartbeat (i.e. connectivity to masterdb)
db.define_table('device_heartbeat',
                Field('at_time', 'datetime', required=True),
                Field('device', 'reference device', required=True, requires=IS_IN_DB(db, 'device.id')),
                Field('site', 'reference site', required=True, requires=IS_IN_DB(db, 'site.id')),
                Field('ip_address', 'string') )

# device history table
db.define_table('device_history',
                 Field('device', 'reference device', label=T('Device'), required=True, requires=IS_IN_DB(db,'device.id','%(make)s/%(model)s')),
                 Field('site', 'reference site', label=T('Site'), required=True, requires=IS_IN_DB(db,'site.id','%(name)s')),
                 Field('time_used', 'datetime', label=T('Used at')),
                 Field('time_received', 'datetime', label=T('Received at')),
                 Field('patient_id', 'integer'))
