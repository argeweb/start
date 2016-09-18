#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/1/28.
from argeweb.core.ndb import decode_key


class ParamInfo(object):
    def __init__(self, request):
        """ easy way to get param from request

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        self.request = request

    def get_ndb_record(self, key="", default_value=None):
        """ get from request and try to parse to a int

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        if key is "":
            return default_value
        try:
            if key not in self.request.params:
                return default_value
            return decode_key(self.request.get(key)).get()
        except:
            return default_value

    def get_integer(self, key="", default_value=0):
        """ get from request and try to parse to a int

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        if key is "":
            return default_value
        try:
            if key not in self.request.params:
                return default_value
            _a = self.request.get(key) if int(self.request.get(key)) is not None else u''
            return default_value if _a == '' else int(_a)
        except:
            return default_value

    def get_float(self, key="", default_value=0.0):
        """ get from request and try to parse to a float

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        if key is "":
            return default_value
        try:
            if key not in self.request.params:
                return default_value
            _a = self.request.get(key) if float(self.request.get(key)) is not None else u''
            if _a == '' or _a == u'':
                _a = default_value
            return default_value if _a == '' else float(_a)
        except:
            return default_value

    def get_string(self, key="", default_value=u''):
        """ get from request and try to parse to a str(unicode)

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        if key is "":
            return default_value
        try:
            if key not in self.request.params:
                rv = default_value
            else:
                rv = self.request.get(key)
        except:
            rv = default_value
        if rv is None or rv is '' or rv is u"":
            rv = u""
        return rv

    def get_header(self, key="", default_value=u''):
        """ get from request and try to parse to a str(unicode)

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        if key is "":
            return default_value
        try:
            if key not in self.request.headers.keys():
                rv = default_value
            else:
                rv = self.request.headers.get(key)
        except:
            rv = default_value
        if rv is None or rv is '' or rv is u"":
            rv = u""
        return rv

    def get_boolean(self, key="", default_value=False):
        """ get from request and try to parse to a bool

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        if key is "":
            return default_value
        try:
            if key not in self.request.params:
                return default_value
            else:
                return bool(self.request.get(key))
        except:
            return default_value

    def get_list(self, key="", exactly_equal=True, use_dict=False):
        """ get from request and try to parse to a list

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        list = []
        if key is not "":
            for item in self.request.POST.multi._items:
                if exactly_equal:
                    if item[0] == key:
                        if use_dict:
                            list.append({"key": str(item[0]), "value": str(item[1])})
                        else:
                            list.append(item[1])
                else:
                    if item[0].find(key) >= 0:
                        if use_dict:
                            list.append({"key": str(item[0]), "value": str(item[1])})
                        else:
                            list.append(item[1])
        return list

    def get_json(self, key=""):
        try:
            import simplejson as json
        except ImportError:
            import json

        if key is "":
            return {}
        data = self.request.get(key)
        return json.loads(data)

    def get_search(self):
        """ get from request and try to parse to a list

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        search_str = []
        for i in xrange(10):
            if self.request.get('search[%s][type]' % i) == 'text' and self.request.get('search[%s][value]' % i) != '':
                search_str.append({
                    "value": u"" + self.request.get('search[%s][value]' % i).replace(u"'", u"''"),
                    "field": u"" + self.request.get('search[%s][field]' % i),
                    "type": u"" + self.request.get('search[%s][type]' % i),
                    "operator": u"" + self.request.get('search[%s][operator]' % i),
                })
        return search_str

    def get_mobile_number(self, key="", default_value=u'', taiwan_format=True):
        """ get from request and try to parse to a str(unicode)

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        if key is "":
            return default_value
        try:
            if key not in self.request.params:
                rv = default_value
            else:
                rv = self.request.get(key)
        except:
            rv = default_value
        if rv is '' or rv is u"":
            return None
        else:
            if len(rv) != 10 or rv.startswith("09") is False:
                return None
        if taiwan_format:
            rv = "+886" + rv[1:]
        return rv

    def string_is_empty(self, key=""):
        key = key.strip()
        if key is None or key is '' or key is u"":
            return True
        else:
            return False

    def get_base64(self, key="", default_value=None):
        """ get from request and try to parse to a str(unicode)

        Args:
            key: the key to get from request
            default_value: then value not exits return
        """
        import base64
        if key is "":
            return default_value
        try:
            if key not in self.request.params:
                rv = default_value
            else:
                rv = self.request.get(key)
        except:
            rv = default_value
        if rv is None or rv is '' or rv is u"":
            return None
        return base64.urlsafe_b64decode(str(rv))

