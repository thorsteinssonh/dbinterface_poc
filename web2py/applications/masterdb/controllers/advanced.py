# -*- coding: utf-8 -*-

from applications.masterdb.modules.language_session import LanguageSession
from sqlite3 import OperationalError

@auth.requires_membership('manager')
@LanguageSession
def index():
    form = SQLFORM.factory(Field('query_name','string', required=False, notnull=True),
                           Field('sql_query','text', required=True, notnull=True,
                                 requires=IS_NOT_EMPTY(error_message="Please enter a query")),
                           submit_button=T('Run query'))
    form.element('textarea[name=sql_query]')['_style'] = 'height:120px;'
    if form.process(keepvalues=True).accepted:
        try:
            sql_result = db.executesql(form.vars.sql_query, as_dict=True)
        except OperationalError as sql_error:
            response.flash = "sql query failed"
            sql_result = None
        else:
            sql_error = None
    else:
        sql_result = None
        sql_error = None
    return locals()
