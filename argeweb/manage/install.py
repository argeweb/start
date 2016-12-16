#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


def run(str_command):
    print str_command
    os.system(str_command)


def main():
    argv = []
    if len(sys.argv) == 1:
        plugin = raw_input('Please enter plugin name: ')
        if plugin.find('=') < 0:
            if plugin.startswith('argeweb/plugin-') is True:
                plugin = '_'.join(plugin.split('-')[1:]) + '=' + plugin
                argv.append(plugin)
            else:
                argv.append(plugin)
    else:
        for n in xrange(0, len(sys.argv)):
            arg = str(sys.argv[n])
            if n == 0:
                continue
            if n == 1 and arg.find('=') < 0:
                if arg.startswith('argeweb/plugin-') is True:
                    arg = '_'.join(arg.split('-')[1:]) + '=' + arg
            if (n == 1 and len(sys.argv) == 2) or (n == 1 and len(sys.argv) == 3 and str(sys.argv[2]) == '-S'):
                print n, len(sys.argv)
                if arg.find('/') < 0 and arg.find('=') < 0 and arg.find('argeweb') < 0:
                    arg = arg + '=argeweb/plugin-' + arg
            argv.append(arg)

    plugins_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',  'plugins')
    os.chdir(plugins_dir)
    run('bower install ' + ' '.join(argv))


if __name__ == '__main__':
    main()