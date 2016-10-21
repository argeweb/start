#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


def run(str_command):
    print str_command
    os.system(str_command)


def main():
    argv = []
    for n in xrange(0, len(sys.argv)):
        arg = str(sys.argv[n])
        if n == 1 and arg.find("=") < 0:
            if arg.startswith("argeweb/plugin-") is True:
                arg = "_".join(arg.split("-")[1:]) + "=" + arg
                argv.append(arg)
            else:
                argv.append(arg)

    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
    os.chdir(dir)
    print argv
    run("bower install " + " ".join(argv) + " -save")


if __name__ == "__main__":
    main()