# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

# Pages

def home():
    return locals()

@auth.requires_login()
def insert():
    db.device_history.time_used.default = request.now
#    db.device_history.....writable = False
#    db.device_history.....readable = False
    form = SQLFORM(db.device_history).process()
    if form.accepted:
        response.flash = "success"
    return locals()

def lookup():
    form = FORM('Testform',
                 INPUT( _name='start', _type='datetime'))
    entries = db(db.device_history).select()
    return locals()

def manage():
    grid = SQLFORM.grid(db.device_history)
    return locals()


def listing():
    response.title = "web2py sample listing"

    # define header and footers:
    head = THEAD(TR(TH("Header 1", _width="50%"), 
                    TH("Header 2", _width="30%"),
                    TH("Header 3", _width="20%"), 
                    _bgcolor="#A0A0A0"))
    foot = TFOOT(TR(TH("Footer 1", _width="50%"), 
                    TH("Footer 2", _width="30%"),
                    TH("Footer 3", _width="20%"),
                    _bgcolor="#E0E0E0"))

    # create several rows:
    rows = []
    for i in range(1000):
        col = i % 2 and "#F0F0F0" or "#FFFFFF"
        rows.append(TR(TD("Row %s" %i),
                       TD("something", _align="center"),
                       TD("%s" % i, _align="right"),
                       _bgcolor=col)) 

    # make the table object
    body = TBODY(*rows)
    table = TABLE(*[head, foot, body], 
                  _border="1", _align="center", _width="100%")

    if request.extension == "pdf":
        from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # define our FPDF class (move to modules if it is reused frequently)
        class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                self.set_font('Arial', 'B', 15)
                self.cell(0, 10, response.title, 1, 0, 'C')
                self.ln(20)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0, 10, txt, 0, 0, 'C')

        pdf = MyFPDF()
        # first page:
        pdf.add_page()
        pdf.write_html(str(XML(table, sanitize=False)))
        response.headers['Content-Type'] = 'application/pdf'
        return pdf.output(dest='S')
    else:
        # normal html view:
        return dict(table=table)





# RPC services
import xmlrpclib, datetime

@service.xmlrpc
def rpc_insert(data):
    unmarshal(data)
    db.device_history.insert(**data)

def unmarshal(data):
    """ perform any uncompleted data conversions for DAL.
        E.g. xmlrpclib communications leave unconverted datetime."""
    for key in data:
        if isinstance(data[key], xmlrpclib.DateTime):
            data[key] = datetime.datetime.strptime(data[key].value, "%Y%m%dT%H:%M:%S")

@service.xmlrpc
def rpc_remove(k):
    db.device_history(k).delete_record()

@service.xmlrpc
def rpc_drop():
    db.device_history.drop()

@service.xmlrpc
def rpc_get(k):
    record = db.device_history(k)
    if record:
        return record.as_dict()
    else:
        return None

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()
