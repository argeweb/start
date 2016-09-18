#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytz
from argeweb.core import settings

def utc_tz():
    return pytz.timezone('UTC')


def local_tz():
    s = pytz.timezone(settings.get('timezone')['local'])
    return s


def localize(dt, tz=None):
    if not dt.tzinfo:
        dt = utc_tz().localize(dt)
    if not tz:
        tz = local_tz()
    return dt.astimezone(tz)
