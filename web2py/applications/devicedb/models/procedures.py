# -*- coding: utf-8 -*-

# SQL request history
db.define_table('query_history',
                Field('query_name','string', required=False, notnull=True),
                Field('sql_query','text', required=True, notnull=True))

# Bulletin schedules
BulletinContentType = ('device history summary','device status summary')
db.define_table('bulletin',
                Field('trigger_expression', 'string'),
                Field('content_type', 'string',
                      requires=IS_IN_SET(BulletinContentType)),
                Field('to_user', 'reference auth_user',
                     requires=IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s')),
                Field('medium', 'string',
                      requires=IS_IN_SET(('email','sms'))),
                Field('is_active', 'boolean', default=True, notnull=True) )
