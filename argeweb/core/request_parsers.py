#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inspect
import json


_parsers = {}


def factory(name):
    """
    Returns a constructed request parser instance by name
    """
    global _parsers
    if inspect.isclass(name):
        return name
    return _parsers.get(name.lower(), _parsers.get(name.lower() + 'parser'))()


class RequestParser(object):
    container_name = None

    class __metaclass__(type):
        def __new__(meta, name, bases, dict):
            global _parsers
            cls = type.__new__(meta, name, bases, dict)
            if name != 'RequestParser':
                _parsers[name.lower()] = cls
            return cls

    def __init__(self):
        self.container = None
        self.fallback = None
        self.data = None
        self.errors = None

    def process(self, request, container, fallback):
        raise NotImplementedError()

    def update(self, obj):
        raise NotImplementedError()

    def validate(self):
        return True


from .json_util import parse as parse_json


class FormParser(RequestParser):
    container_name = 'Form'

    def process(self, request, container, fallback=None):
        from argeweb.libs.wtforms_json import MultiDict, flatten_json

        if inspect.isclass(container):
            container = container()

        if request.content_type == 'application/json':
            request_data = MultiDict(flatten_json(container.__class__, parse_json(request.body)))
        elif request.method in ('GET'):
            request_data = None
        else:
            request_data = request.params

        container.process(formdata=request_data, obj=fallback, **container.data)

        self.container = container
        self.fallback = fallback

        return self

    def update(self, obj):
        self.container.populate_obj(obj)
        return obj

    def validate(self):
        return self.container.validate() if self.container else False

    def _get_data(self):
        return self.container.data if self.container else None

    def _set_data(self, val):
        if self.container:
            self.container.data = val

    data = property(_get_data, _set_data)

    def _get_errors(self):
        return self.container.errors if self.container else None

    errors = property(_get_errors, lambda s, v: None)
