#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/10/10


from argeweb.core.ndb import Model, BasicModel, ndb
from argeweb.core import property as Fields


class HostInformationModel(BasicModel):
    class Meta:
        label_name = {
            "host": u"域名",
            "namespace": u"命名空間",
            "site_name": u"",
            "plugins": u"命名空間",
            "is_lock": u"命名空間",
        }
    host = Fields.StringProperty(required=True)
    namespace = Fields.StringProperty(required=True)
    site_name = Fields.StringProperty()
    plugins = Fields.StringProperty()
    theme = Fields.StringProperty()
    is_lock = Fields.BooleanProperty(default=True)

    def plugins_list(self):
        return str(self.plugins).split(",")

    @classmethod
    def get_by_host(cls, host):
        q = cls.query(cls.host == host).get_async()
        return q.get_result()

    @classmethod
    def get_by_namespace(cls, namespace):
        return cls.query(cls.namespace == namespace).get()

    @classmethod
    def get_or_insert(cls, host, theme=None, plugins=None, is_lock=True):
        item = cls.get_by_host(host)
        if item is None:
            import random, string
            item = cls()
            item.host = host
            r = ''.join(random.choice(string.lowercase) for i in range(25))
            item.namespace = u"%s-%s-%s-%s" % (r[0:4], r[5:9], r[10:14], r[15:19])
            item.theme = theme if theme is not None else u""
            item.plugins = plugins if plugins is not None else u""
            item.is_lock = is_lock
            item.put()
        return item


class WebSettingModel(BasicModel):
    class Meta:
        label_name = {
            "setting_name": u"名稱",
            "setting_key": u"鍵",
            "setting_value": u"值",
        }
    setting_name = Fields.StringProperty()
    setting_key = Fields.StringProperty(required=True)
    setting_value = Fields.StringProperty(required=True)

    @classmethod
    def get_by_key(cls, key):
        return cls.query(cls.setting_key == key).get()

    @classmethod
    def get_or_insert(cls, key, default):
        item = cls.query(cls.setting_key == key).get()
        if item is None:
            item = cls()
            item.setting_key = key
            item.setting_value = default
            item.put()
        return item
