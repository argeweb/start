#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/07/11


_function_list = {}

def register(function_object=None, prefix=u"global"):
    name = prefix + ":" + function_object.__name__
    if name in _function_list:
        return
    _function_list[name] = function_object


class Function(object):
    _controller = None

    def __init__(self, controller):
        self._controller = controller

    def get_run(self):
        def run(common_name, *args, **kwargs):
            prefix = u"global"
            if kwargs.has_key("function_prefix"):
                prefix = kwargs["function_prefix"]
            name = prefix + ":" + common_name
            if name in _function_list:
                return _function_list[name](*args, **kwargs)
        return run

