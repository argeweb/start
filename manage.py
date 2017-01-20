#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


def change_dir(dir_path):
    print dir_path
    os.chdir(dir_path)


def run(str_command):
    print str_command
    os.system(str_command)

script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
argeweb_dir = os.path.join(script_dir, 'argeweb')
plugins_dir = os.path.join(script_dir, 'plugins')
manage_dir = os.path.join(argeweb_dir, 'manage')

action = ""
argv = []

for n in xrange(0, len(sys.argv)):
    arg = str(sys.argv[n])
    if n == 1:
        action = arg
    else:
        if n >= 2:
            if arg.find("http") >=0:
                argv.append('"' + arg + '"')
            else:
                argv.append(arg)


def update(argv):
    if len(argv) == 0:
        change_dir(argeweb_dir)
        run('bower update')

        change_dir(plugins_dir)
        run('bower update')

        # target_dir = os.path.join(base_dir, 'static')
        # os.chdir(target_dir)
        # run('bower update')
        # run('bower list --paths --json > bower_path.json')
    else:
        bower_argv = []
        for n in xrange(0, len(argv)):
            arg = str(argv[n])
            if n == 1 and arg.find('=') < 0:
                if arg.startswith('argeweb/plugin-') is True:
                    arg = '_'.join(arg.split('-')[1:]) + '=' + arg
                    bower_argv.append(arg)
                else:
                    bower_argv.append(arg)

        change_dir(plugins_dir)
        run('bower update ' + ' '.join(bower_argv) + '')


if action != 'update':
    change_dir(manage_dir)
    run("%s.py %s" % (action, " ".join(argv)))
else:
    update(argv)

