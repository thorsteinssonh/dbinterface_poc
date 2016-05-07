# -*- coding: utf-8 -*-

from applications.masterdb.modules.language_session import LanguageSession

@auth.requires_membership('manager')
@LanguageSession
def index():
    #form = FORM('Your name:', INPUT(_name='name'), INPUT(_type='submit'))
    #return dict(form=form)
    form = SQLFORM(db.advanced_sql_history).process()
    if form.accepted:
        response.flash = "success"
    return locals()
