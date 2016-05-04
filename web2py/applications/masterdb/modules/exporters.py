#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
from gluon.html import xmlescape
from gluon.sqlhtml import ExportClass
from gluon.contrib.pyfpdf import FPDF, HTMLMixin
from datetime import datetime
import re

class MDBExporterPDF(ExportClass):
    label = 'PDF'
    file_ext = "pdf"
    content_type = "application/pdf"

    # behavior vars
    title = "Missing Title"
    request = None
    session = None
    
    def __init__(self, rows):
        ExportClass.__init__(self, rows)
        
    def create_header(self, colnames):
        th = []
        for n in colnames:
            wstr = "%.0f%%"%(100.0/len(colnames))
            th.append( TH(n, _width=wstr) )
        return THEAD( TR( *th, _bgcolor="#A0A0A0") )
    
    def serialize_row(self, row):
        data = []
        for n in row.keys():
            data.append( str(row.get(n)) )
        return data
    
    def create_row(self, row, bg="#FFFFFF"):
        td = []
        for d in self.serialize_row(row):
            td.append( TD( d ) )
        return TR( *td, _bgcolor=bg )
    
    def export(self):
        if self.rows:
            pdf = MyFPDF(title=self.title)
            pdf.setFont(1)
            pdf.textBox("Something here...", prop='right', 
                        justify='L', border=False)
            pdf.textBox("Date: "+datetime.now().strftime("%Y %m %d"),
                        justify='R', prop='return')

            # if request object attached, look for keyword search terms of the data
            if self.request and self.request.vars.keywords:
                pdf.textBox("Search term: "+self.request.vars.keywords, justify='L')
            pdf.newLine()
            pdf.smBorder = True
            pdf.smJustify = 'L'
            pdf.textBoxMultiRow( dict(zip(self.rows[0].keys(),self.rows[0].keys())) )
            for row in self.rows:
                pdf.textBoxMultiRow(row)

            mystr = '哪裡是我的朋友，他在做什麼>的東西BYEBYE'
            pdf.textBoxMulti(mystr)

            return pdf.output(dest='S')
        else:
            return 'null'

def hasCJK(s):
    """ check if utf8 interpreted sting has asian CJK pictogram chars """
    if re.search(u"([\u4e00-\uffff]+.*?)", s.decode('utf8')):
        return True
    else:
        return False

# define our FPDF class (move to modules if it is reused frequently)
class MyFPDF(FPDF):
    # state machine like vars
    smJustify = 'L'
    smBorder = 0
    smBg = "#FFFFFF"
    smW = 0
    smH = 0
    smFont = 'Arial'
    smZhTwFont = "zh-tw"
    smEnFont = 'Arial'
    smHeadingIdx = 0
    smHeadings =[('B',15),
                 ('',12),
                 ('I',8)]
    smProp = 'return'
    smPropDict = {'return':1,
                  'right':0,
                  'below':2}
    smBoxMultiLineH = 0
    smTitle=""
    smLang=None
    
    def __init__(self, title="No Title", lang=None):
        FPDF.__init__(self)
        self.smTitle = title
        self.smLang = lang
        self.set_title(self.smTitle)
        
        # Note zh fonts take time to load -- look into a singleton solution...
        self.add_font('zh-tw','','SourceHanSansTC-Regular.ttf', uni=True)
        self.add_font('zh-tw','B','SourceHanSansTC-Bold.ttf', uni=True)
        self.add_font('zh-tw','I','SourceHanSansTC-Regular.ttf', uni=True)
        
        # first page:
        self.add_page()
    
    def setFont(self, idx):
        self.smHeadingIdx = idx
        self.smH = int(self.smHeadings[idx][1]*0.6)
        self.set_font(self.smFont, *self.smHeadings[idx])
    
    def bgColor(self, color):
        pass

    def newLine(self):
        self.ln(self.smH)
    
    def textBoxMultiRow(self, row, styles=None):
        if styles == None:
            # create default styles
            keys = row.keys()
            styles = []
            for k in keys:
                styles.append( ({'key':k,'wf':1.0/len(keys)}) )
        # now print a multi box for each key value in row
        for i, s in enumerate(styles):
            key = s['key']
            if i<len(styles)-1: prop = 'right'
            else: prop = 'return'
            self.textBoxMulti(str(row[key]),wf=s['wf'], prop=prop)

    def fontSwitching(self,txt):
        # if string has CJK unicode char then switch font
        if hasCJK(txt):
            self.smFont = self.smZhTwFont
            self.setFont(self.smHeadingIdx)
        else:
            self.smFont = self.smEnFont
            self.setFont(self.smHeadingIdx)
            
    def textBoxMulti(self, txt, wf=None, w=None, h=None, border=None, justify=None, prop=None):
        if wf is not None: self.smW = wf*( self.w - self.r_margin - self.l_margin )
        if w is not None: self.smW = w
        if h is not None: self.smH = h
        if border is not None: self.smBorder = border
        if justify is not None: self.smJustify = justify
        if prop is not None: self.smProp = prop
        x_bf = self.get_x()
        y_bf = self.get_y()
        # draw the text box
        self.fontSwitching(txt)
        self.multi_cell(self.smW, self.smH,
                        txt, self.smBorder, self.smJustify, fill=False)
        x_af = self.get_x()
        y_af = self.get_y()
        dy = y_af - y_bf
        # handle cursor propagation
        if self.smProp == "right":
            self.set_y(y_bf)
            self.set_x(x_bf+self.smW)
            if self.smBoxMultiLineH < dy:
                self.smBoxMultiLineH = dy
        elif self.smProp == "return":
            self.set_y(y_bf + self.smBoxMultiLineH)
            self.smBoxMultiLineH = dy
    
    def textBox(self, txt, wf=None, w=None, h=None, border=None, justify=None, prop=None):
        if wf is not None: self.smW = w*wf
        if w is not None: self.smW = w
        if h is not None: self.smH = h
        if border is not None: self.smBorder = border
        if justify is not None: self.smJustify = justify
        if prop is not None: self.smProp = prop
        self.fontSwitching(txt)
        self.cell(self.smW, self.smH,
                  txt, self.smBorder,
                  self.smPropDict[self.smProp], self.smJustify, fill=False)
    
    def header(self):
        self.setFont(0)
        self.textBox(self.smTitle, border='B')
        self.newLine()

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        txt = '%s -- page %s of %s' % (self.smTitle, self.page_no(), self.alias_nb_pages())
        self.cell(0, 10, txt, 0, 0, 'C')
