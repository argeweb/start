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
        target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
        os.chdir(target_dir)
        run("bower update")
        target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        os.chdir(target_dir)
        run("bower update")
    else:
        for n in xrange(0, len(sys.argv)):
            arg = str(sys.argv[n])
            if n == 1 and arg.find("=") < 0:
                if arg.startswith("argeweb/plugin-") is True:
                    print arg
                    arg = "_".join(arg.split("-")[1:]) + "=" + arg
                    argv.append(arg)
                else:
                    argv.append(arg)

        target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')
        os.chdir(target_dir)
        run("bower update " + " ".join(argv) + "")


if __name__ == "__main__":
    main()