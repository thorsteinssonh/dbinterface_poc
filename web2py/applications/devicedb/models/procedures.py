# -*- coding: utf-8 -*-
from bulletin import BulletinContentType, IS_TRIGGER_EXPR

# SQL request history
db.define_table('query_history',
                Field('query_name','string', required=False, notnull=True),
                Field('sql_query','text', required=True, notnull=True))

# Bulletin schedules

db.define_table('bulletin',
                Field('trigger_expression', 'string',
                      requires=IS_TRIGGER_EXPR()),
                Field('content_type', 'string',
                      requires=IS_IN_SET(BulletinContentType)),
                Field('to_user', 'reference auth_user',
                     requires=IS_IN_DB(db,'auth_user.id','%(first_name)s %(last_name)s')),
                Field('medium', 'string',
                      requires=IS_IN_SET(('email','sms'))),
                Field('is_active', 'boolean', default=True, notnull=True),
                Field('last_execution', 'datetime'))
