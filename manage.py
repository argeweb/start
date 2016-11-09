#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


def run(str_command):
    print str_command
    os.system(str_command)

manage_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "argeweb",  "manage")
os.chdir(manage_dir)
action = ""
argv = []
for n in xrange(0, len(sys.argv)):
    arg = str(sys.argv[n])
    if n == 1:
        action = arg
    else:
        if n >= 2:
            argv.append(arg)
run("%s.py %s" % (action, " ".join(argv)))
