#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
from gluon.html import xmlescape
from gluon.sqlhtml import ExportClass
from gluon.contrib.pyfpdf import FPDF
from datetime import datetime
import re

class MDBExporterPDF(ExportClass):
    label = 'PDF'
    file_ext = "pdf"
    content_type = "application/pdf"

    # behavior vars
    title = "Missing Title"
    search_keywords = None
    row_key_styles = None
    
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
            pdf.setFont('h2')
            pdf.textBox("CHC Master Database", prop='right',
                        justify='L', border=False)
            pdf.setFont('h3')
            pdf.textBox(datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                        justify='R', prop='return')

            # if request object attached, look for keyword search terms of the data
            if self.search_keywords:
                pdf.setFont('h3i')
                pdf.textBox("Search term: "+self.search_keywords, justify='L')
            pdf.newLine()
            pdf.smBorder = True
            pdf.smJustify = 'L'
            pdf.setFont('th')
            pdf.setLineWidth(0.1)
            pdf.textBoxMultiRow( dict(zip(self.rows[0].keys(),self.rows[0].keys())),
                                 styles = self.row_key_styles,
                                 fill_color=(255,255,255), use_fmt=False)
            pdf.setFont('td')
            pdf.saveState()
            for row in self.rows:
                pdf.textBoxMultiRow(row, styles = self.row_key_styles)

            return pdf.output(dest='S')
        else:
            return 'null'

def hasCJK(s):
    """ check if utf8 interpreted string has asian CJK pictogram chars """
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
    smHeadingKey = 'h1'
    smHeadings ={'h1':('B',15),
                 'h2':('B',12),
                 'h3':('',12),
                 'h3i':('I',12),
                 'th':('B',10),
                 'td':('',10),
                 'footnote':('I',8)}
    smProp = 'return'
    smPropDict = {'return':1,
                  'right':0,
                  'below':2}
    smBoxMultiLineH = 0
    smTitle=""
    smLang=None
    smMultiRowFill = ((255,255,255),
                      (240,240,240))
    smMultiRowCounter = 0
    smSavedState = None
    __instance = None
    
    def __init__(self, title="No Title", lang=None):
        FPDF.__init__(self)
        self.smTitle = str(title)
        self.smLang = lang
        self.set_title("Data Export")
        
        # first page:
        self.add_page()
    
    def loadZhTwFonts(self):
        # Note zh fonts take time to load
        if 'SourceHanSansTC-Regular.ttf' not in self.font_files:
            self.add_font('zh-tw','','SourceHanSansTC-Regular.ttf', uni=True)
            self.add_font('zh-tw','B','SourceHanSansTC-Bold.ttf', uni=True)
            self.add_font('zh-tw','I','SourceHanSansTC-Regular.ttf', uni=True)

    @staticmethod
    def singleton(title="No Title"):
        # singleton instance factory ( Bug: not clearing pdf data )
        if MyFPDF.__instance is None:
            MyFPDF.__instance = MyFPDF(title=title)
        return MyFPDF.__instance
    
    def setFont(self, key):
        self.smHeadingKey = key
        self.smH = int(self.smHeadings[key][1]*0.6)
        self.set_font(self.smFont, *self.smHeadings[key])
    
    def setLineWidth(self,width):
        self.set_line_width(width)

    def newLine(self,factor=1.0):
        self.ln(self.smH*factor)
    
    def textBoxMultiRow(self, row, styles=None, fill_color=None, use_fmt=True):
        # add new page if measured necessary
        # avoid writing row across page break
        if self.get_y() + 3*self.smBoxMultiLineH > self.page_break_trigger:
            self.add_page()
        # default styling
        if styles == None:
            # create default styles
            keys = row.keys()
            styles = []
            for k in keys:
                styles.append( {'key':k,'wf':1.0/len(keys),
                                 'border':True,
                                 'fmt':lambda x: x} )
        else:
            # some other defaults
            for s in styles:
                if 'wf' not in s.keys(): s['wf'] = 1.0/len(styles)
                if 'border' not in s.keys(): s['border'] = True
                if 'fmt' not in s.keys(): s['fmt'] = lambda x: x
        # semi-dry run to measure multi cell height ...
        x_bf = self.get_x()
        y_bf = self.get_y()
        for i, s in enumerate(styles):
            key = s['key']
            if i<len(styles)-1: prop = 'right'
            else: prop = 'return'
            if use_fmt: txt = str(s['fmt'](row[key]))
            else: txt = str(row[key])
            self.textBoxMulti(txt, wf=s['wf'], prop=prop, border=False)
        x_af = self.get_x()
        y_af = self.get_y()
        dy = y_af-y_bf
        # now print a multi cell for each key value in row
        self.set_xy(x_bf, y_bf)
        if self.smMultiRowFill is not None:
            self.smMultiRowCounter+=1
            self.set_fill_color( *self.smMultiRowFill[self.smMultiRowCounter%2] )
            fill=True
        if fill_color is not None:
            self.set_fill_color( *fill_color )
            fill=True
        for i, s in enumerate(styles):
            key = s['key']
            if i<len(styles)-1: prop = 'right'
            else: prop = 'return'
            x = self.get_x()
            y = self.get_y()
            w = s['wf']*( self.w - self.r_margin - self.l_margin )
            h = dy
            self.drawBox(x,y,w,h, style=s['border'], fill=fill)
            if use_fmt: txt = str(s['fmt'](row[key]))
            else: txt = str(row[key])
            self.textBoxMulti(txt, wf=s['wf'], prop=prop)

    def drawBox(self, x, y, w, h, style=True, fill=False):
        if fill:
            # quickfix padding '0.1' to stop gaps forming
            self.rect(x,y,w+0.1,h+0.1,'F')
        if style == 1 or 'L' in style:
            self.line(x,y,x,y+h)
        if style == 1 or 'R' in style:
            self.line(x+w,y,x+w,y+h)
        if style == 1 or 'T' in style:
            self.line(x,y,x+w,y)
        if style == 1 or 'B' in style:
            self.line(x,y+h,x+w,y+h)
        
    def fontSwitching(self,txt):
        # if string has CJK unicode char then switch font
        if hasCJK(txt):
            self.loadZhTwFonts()
            self.smFont = self.smZhTwFont
            self.setFont(self.smHeadingKey)
        else:
            self.smFont = self.smEnFont
            self.setFont(self.smHeadingKey)
            
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
        if wf is not None: self.smW = wf*( self.w - self.r_margin - self.l_margin )
        if w is not None: self.smW = w
        if h is not None: self.smH = h
        if border is not None: self.smBorder = border
        if justify is not None: self.smJustify = justify
        if prop is not None: self.smProp = prop
        self.fontSwitching(txt)
        self.cell(self.smW, self.smH,
                  str(txt), self.smBorder,
                  self.smPropDict[self.smProp], self.smJustify, fill=False)
        
    def saveState(self):
        s = []
        # state machine like vars
        s.append(self.smJustify)
        s.append(self.smBorder)
        s.append(self.smW)
        s.append(self.smH)
        s.append(self.smFont)
        s.append(self.smZhTwFont)
        s.append(self.smEnFont)
        s.append(self.smHeadingKey)
        s.append(self.smProp)
        s.append(self.smBoxMultiLineH)
        self.smSavedState = s

    def restoreState(self):
        s = self.smSavedState
        if s is None or len(s) == 0:
            return
        # state machine like vars
        self.smJustify = s[0]
        self.smBorder = s[1]
        self.smW = s[2]
        self.smH = s[3]
        self.smFont = s[4]
        self.smZhTwFont = s[5]
        self.smEnFont = s[6]
        self.smHeadingKey = s[7]
        self.smProp = s[8]
        self.smBoxMultiLineH = s[9]
        # function calls
        self.setFont(self.smHeadingKey)

    def header(self):
        hk = self.smHeadingKey
        self.setFont('h1')
        self.textBox(self.smTitle, w=0, h=0, border='B', prop='return', justify='L')
        self.newLine(0.3)
        self.restoreState()

    def footer(self):
        hk = self.smHeadingKey
        self.set_y(-15)
        self.setFont('footnote')
        txt = '%s -- page %s of %s' % (self.smTitle, self.page_no(), self.alias_nb_pages())
        self.textBox(txt, w=0, h=0, prop='right', border=False, justify='C')
        #self.cell(0, 10, txt, 0, 0, 'C')
        self.setFont(hk)
