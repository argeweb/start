#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from google.appengine.ext import vendor
from argeweb.core.settings import load_settings
load_settings()

vendor.add(
    os.path.join(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'argeweb')
        , 'libs')
    )