"""
WTForms
=======

WTForms is a flexible forms validation and rendering library for python web
development.

:copyright: Copyright (c) 2010 by Thomas Johansson, James Crasta and others.
:license: BSD, see LICENSE.txt for details.
"""
import validators, widgets
from .fields import *
from .form import Form
from .validators import ValidationError

__version__ = '3.0dev'
