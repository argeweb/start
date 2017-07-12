#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def run(str_command):
    print str_command
    os.system(str_command)

run('start chrome http://127.0.0.1:8080')
