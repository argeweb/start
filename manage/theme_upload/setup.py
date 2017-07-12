#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/11/26


from distutils.core import setup
import py2exe
import sys
import certifi

print certifi.where()
sys.argv.append('py2exe')
setup(
    options={'py2exe': dict(bundle_files=1, optimize=2)},
    console=['upload.py'],
    includes=['OpenSSL', 'certifi'],
    zipfile=None,
    data_files=['cacert.pem'],
    ascii=True,
    dll_excludes=['msvcr71.dll'],
    compressed=True,
)
