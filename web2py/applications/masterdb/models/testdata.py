# -*- coding: utf-8 -*-


db.define_table('testdata',
                Field('hospital', requires=IS_NOT_EMPTY()),
                Field('equipment', requires=IS_NOT_EMPTY()),
                Field('created_on', 'datetime'),
                auth.signature)

db.define_table('testdata_comments',
                Field('testdata', 'reference testdata'),
                Field('comment_text', 'text', requires=IS_NOT_EMPTY()),
                auth.signature)

# auth.signature field takes care of following automatically
#                Field('created_by', 'reference auth_user'),
#                Field('modified_by', 'reference auth_user'),
#                Field('modified_on', 'datetime'))
