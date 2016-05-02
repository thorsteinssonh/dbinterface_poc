#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

def LanguageSession(f):
    if f.func_globals['request'].vars.lang:
        f.func_globals['session'].session_language = f.func_globals['request'].vars.lang
    
    if f.func_globals['session'].session_language:
        f.func_globals['T'].force( f.func_globals['session'].session_language )
    return f
