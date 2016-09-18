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
        from argeweb.core.wtforms.wtforms_json import MultiDict, flatten_json

        if inspect.isclass(container):
            container = container()

        if request.content_type == 'application/json':
            request_data = MultiDict(flatten_json(container.__class__, parse_json(request.body)))
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


class MessageParser(RequestParser):
    container_name = 'Message'

    def __init__(self):
        super(MessageParser, self).__init__()
        self.partial_fields = None

    def process(self, request, container, fallback=None):
        from protorpc import protojson, messages

        try:
            self.partial_fields = json.loads(request.body).keys()
            result = protojson.decode_message(container, request.body)
            self.errors = None

        except (messages.ValidationError, ValueError) as e:
            result = container()
            self.errors = [e.message]
            self.partial_fields = None

        self.container = result
        self.fallback = fallback
        return self

    def validate(self):
        return not self.errors and self.container.is_initialized() if self.container else False

    def update(self, obj):
        from .messages import to_entity
        return to_entity(self.container, obj, only=self.partial_fields)
