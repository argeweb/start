#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/07/11


_commands = {}


def register(name, common_object=None):
    if name in _commands:
        return
    _commands[name] = common_object


class Datastore(object):
    _controller = None

    def __init__(self, controller):
        self._controller = controller

    def get(self, name, *args, **kwargs):
        if name in _commands:
            rv = _commands[name](*args, **kwargs)
            try:
                return rv.get()
            except:
                return rv

    def query(self, name, *args, **kwargs):
        if name in _commands:
            query = _commands[name](*args, **kwargs)
            check_near = 3
            if "size" not in kwargs:
                kwargs["size"] = self._controller.params.get_integer("size", 10)
            if "page" not in kwargs:
                kwargs["page"] = self._controller.params.get_integer("page", 1)
            if "near" not in kwargs:
                kwargs["near"] = self._controller.params.get_integer("near", 10)
            if "data_only" not in kwargs:
                kwargs["data_only"] = self._controller.params.get_boolean("data_only", True)
            return self._controller.paging(query, kwargs["size"], kwargs["page"], kwargs["near"], kwargs["data_only"])

    def random(self, cls_name, common_name, size=3, *args, **kwargs):
        import random
        return_lst = []
        cls_name = cls_name + ":" + common_name
        if cls_name not in _commands:
            return return_lst
        query = _commands[cls_name](*args, **kwargs)
        lst = query.fetch(size * 10)
        if len(lst) >= size:
            return_lst = random.sample(lst, size)
        else:
            return_lst = lst
        return return_lst


