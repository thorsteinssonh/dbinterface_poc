# -*- coding: utf-8 -*-


db.define_table('testdata',
                Field('hospital', requires=IS_NOT_EMPTY()),
                Field('equipment', requires=IS_NOT_EMPTY()),
                Field('created_on', 'datetime'))
