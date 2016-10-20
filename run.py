#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def run(str_command):
    print str_command
    os.system(str_command)

dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
os.chdir(dir)
run ("dev_appserver.py .")
