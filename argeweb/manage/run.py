#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def run(str_command):
    print str_command
    os.system(str_command)

def main():
    dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',  '..')
    os.chdir(dir)
    run('start chrome http://127.0.0.1:8080')
    run('dev_appserver.py . --host=127.0.0.1')

if __name__ == '__main__':
    main()