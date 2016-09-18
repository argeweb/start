#!/usr/bin/env python
# -*- coding: utf-8 -*-
from webapp2 import Response
import json


_handlers = {}


def factory(kind):
    """
    Returns a ResponseHandler instance based on which type it can handle.
    """
    global _handlers
    if kind in _handlers:
        return _handlers[kind]()
    for parent_kind in _handlers.keys():
        if issubclass(kind, parent_kind):
            return _handlers[parent_kind]()


class ResponseHandler(object):
    _handlers = {}

    class __metaclass__(type):
        def __new__(meta, name, bases, dict):
            global _handlers
            cls = type.__new__(meta, name, bases, dict)
            if name != 'ResponseHandler':
                _handlers[cls.type] = cls
            return cls

    def process(self, handler, result):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.process(*args, **kwargs)


class ResponseResponseHandler(ResponseHandler):
    type = Response

    def process(self, handler, result):
        return result


class StringResponseHandler(ResponseHandler):
    type = basestring

    def process(self, handler, result):
        handler._clear_redirect()
        handler.response.charset = 'utf-8'
        handler.response.unicode_body = unicode(result)
        if not handler.response.content_type:
            handler.response.content_type = result.content_type if hasattr(result, 'content_type') else 'text/html'
        return handler.response


class TupleResponseHandler(ResponseHandler):
    type = tuple

    def process(self, handler, result):
        handler._clear_redirect()
        handler.response = Response(result)
        return handler.response


class IntResponseHandler(ResponseHandler):
    type = int

    def process(self, handler, result):
        handler._clear_redirect()
        handler.abort(result)


class DictResponseHandler(ResponseHandler):
    type = dict

    def process(self, handler, result):
        handler._clear_redirect()
        handler.response.charset = 'utf-8'
        handler.response.unicode_body = unicode(json.dumps(result, encoding='utf-8', ensure_ascii=False))
        if not handler.response.content_type:
            handler.response.content_type = result.content_type if hasattr(result, 'content_type') else 'text/json'
        return handler.response
