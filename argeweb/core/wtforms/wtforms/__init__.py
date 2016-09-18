"""
WTForms
=======

WTForms is a flexible forms validation and rendering library for python web
development.

:copyright: Copyright (c) 2010 by Thomas Johansson, James Crasta and others.
:license: BSD, see LICENSE.txt for details.
"""
from argeweb.core.wtforms.wtforms import validators, widgets
from argeweb.core.wtforms.wtforms.fields import *
from argeweb.core.wtforms.wtforms.form import Form
from argeweb.core.wtforms.wtforms.validators import ValidationError

__version__ = '2.0dev'
