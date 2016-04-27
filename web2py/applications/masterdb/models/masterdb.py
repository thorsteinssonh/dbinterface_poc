# -*- coding: utf-8 -*-

# treatement centre table
db.define_table('treatment_center',
                Field('name', requires=IS_NOT_EMPTY()),
                Field('country', 'string', requires=IS_NOT_EMPTY()),
                Field('address'))

# medical device table
db.define_table('medical_device',
                Field('device_type', 'string', requires=IS_NOT_EMPTY()),
                Field('make', 'string'),
                Field('model', 'string'),
                Field('serial_no', 'string'))

# device history table
db.define_table('device_history',
                 Field('medical_device', 'reference medical_device', required=True, requires=IS_IN_DB(db,'medical_device.id','%(make)s/%(model)s')),
                 Field('treatment_center', 'reference treatment_center', required=True, requires=IS_IN_DB(db,'treatment_center.id','%(name)s')),
                 Field('time_used', 'datetime'),
                 Field('patient_id', 'integer'))
