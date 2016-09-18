#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2014/9/30
from webapp2 import get_request
import os
import logging
import inspect
from . import events
from argeweb.core.ndb import Model, BasicModel, ndb
from argeweb.core import property as Fields
from google.appengine.api import namespace_manager
from google.appengine.api import memcache

_defaults = {}


class HostInformation(BasicModel):
    class Meta:
        label_name = {
            "host": u"域名",
            "namespace": u"命名空間",
        }
    host = Fields.StringProperty(required=True)
    namespace = Fields.StringProperty(required=True)
    site_name = Fields.StringProperty()
    plugins = Fields.StringProperty()
    theme = Fields.StringProperty()

    def plugins_list(self):
        return str(self.plugins).split(",")

    @classmethod
    def get_by_host(cls, host):
        return cls.query(cls.host == host).get()

    @classmethod
    def get_by_namespace(cls, namespace):
        return cls.query(cls.namespace == namespace).get()

    @classmethod
    def get_or_insert(cls, host, theme=None, plugins=None):
        item = cls.query(cls.host == host).get()
        if item is None:
            import random, string
            item = cls()
            item.host = host
            r = ''.join(random.choice(string.lowercase) for i in range(25))
            item.namespace = u"%s-%s-%s-%s" % (r[0:4], r[5:9], r[10:14], r[15:19])
            item.theme = theme if theme is not None else u""
            item.plugins = plugins if plugins is not None else u""
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


class ConfigurationError(Exception):
    pass


def load_settings(app_settings=None, refresh=False):
    """
    Executed when the project is created and loads the settings from application/settings.py
    """
    global _defaults

    if _defaults and not refresh:
        return
    if app_settings is None:
        try:
            from application import settings as appsettings
            reload(appsettings)
            # try:
            # except ImportError:
            #     raise ConfigurationError("Settings not found. Please create /application/settings.py")
            appdefaults = appsettings.settings
            logging.debug("Static settings loaded from application.settings.py")
        except:
            try:
                from argeweb import base_settings as appsettings
                reload(appsettings)
                # try:
                # except ImportError:
                #     raise ConfigurationError("Settings not found. Please create /application/settings.py")
                appdefaults = appsettings.settings
                logging.debug("Static settings loaded from argeweb.settings.py")
            except AttributeError:
                raise ConfigurationError("No dictionary 'settings' found in settings.py")
    else:
        appdefaults = app_settings
    defaults(appdefaults)


def defaults(dict=None):
    """
    Adds a set of default values to the settings registry. These can and will be updated
    by any settings modules in effect, such as the Settings Manager.

    If dict is None, it'll return the current defaults.
    """
    if dict:
        _defaults.update(dict)
    else:
        return _defaults


def settings():
    """
    Returns the entire settings registry
    """
    settings = {}
    events.fire('before_settings', settings=settings)
    settings.update(_defaults)
    events.fire('after_settings', settings=settings)
    return settings


def print_setting(key):
    return get_from_datastore(key, "")

def get(key, default=None):
    """
    Returns the setting at key, if available, raises an ConfigurationError if default is none, otherwise
    returns the default
    """
    _settings = settings()
    if key in _settings:
        return _settings[key]
    default = os.environ.get(key, default)
    if default is None:
        raise ConfigurationError("Missing setting %s" % key)
    else:
        _defaults.update({key: default})
        return default


def save_to_datastore(setting_key, setting_value, use_memcache=True, prefix=u""):
    _prefix = prefix
    if _prefix is not u"":
        _prefix += "."
    memcache_key = "setting." + _prefix + setting_key
    item = WebSettingModel.get_or_insert(key=setting_key, default=setting_value)
    item.setting_value = setting_value
    item.put()
    if use_memcache:
        memcache.set(key=memcache_key, value=setting_value, time=100)


def get_from_datastore(setting_key, default=None, auto_save=True, use_memcache=True, prefix=u""):
    if default is None:
        default = u""
    _prefix = prefix
    if _prefix is not u"":
        _prefix += "."
    memcache_key = "setting." + _prefix + setting_key
    if use_memcache:
        data = memcache.get(memcache_key)
        if data is not None:
            return data
    if auto_save:
        item = WebSettingModel.get_or_insert(key=setting_key, default=default)
    else:
        item = WebSettingModel.get_by_key(key=setting_key)
    if use_memcache:
        if item is None:
            memcache.add(key=memcache_key, value=default, time=100)
            return default
        else:
            memcache.add(key=memcache_key, value=item.setting_value, time=100)
    return item.setting_value


def get_info(key, memcache_key, host=None, host_item=None, timeout=100):
    if host_item is not None:
        return_string = getattr(host_item, key)
        memcache.set(key=memcache_key, value=return_string, time=timeout)
    else:
        return_string = memcache.get(memcache_key)
        if return_string is None and host_item is None:
            host_item = HostInformation.get_by_host(host)
            if host_item is not None:
                return_string = getattr(host_item, key)
                memcache.set(key=memcache_key, value=return_string, time=timeout)
    return return_string, host_item


def get_plugins(server_name, namespace):
    namespace_manager.set_namespace("shared.host")
    host_item = HostInformation.get_by_host(server_name)
    namespace_manager.set_namespace(namespace)
    return str(host_item.plugins).split(",")


def set_plugins(server_name, namespace, plugins):
    namespace_manager.set_namespace("shared.host")
    host_item = HostInformation.get_by_host(server_name)
    host_item.plugins = ",".join(plugins)
    host_item.put()
    update_memcache(server_name, host_item)
    namespace_manager.set_namespace(namespace)


def get_theme(server_name, namespace):
    namespace_manager.set_namespace("shared.host")
    host_item = HostInformation.get_by_host(server_name)
    namespace_manager.set_namespace(namespace)
    return host_item.theme


def set_theme(server_name, namespace, theme):
    namespace_manager.set_namespace("shared.host")
    host_item = HostInformation.get_by_host(server_name)
    host_item.theme = theme
    host_item.put()
    update_memcache(server_name, host_item)
    namespace_manager.set_namespace(namespace)


def get_host_item(server_name):
    namespace_manager.set_namespace("shared.host")
    memcache_key = "shared.host.info." + server_name
    host_item = memcache.get(memcache_key)
    if host_item is None:
        host_item = HostInformation.get_or_insert(
            host=server_name,
            theme="install",
            plugins="application_user,application_user_role,backend_ui_material,scaffold,themes,web_file,web_page,web_setting,plugin_manager"
        )
    return update_memcache(server_name, host_item)


def update_memcache(server_name, host_item=None):
    namespace_manager.set_namespace("shared.host")
    memcache_key = "shared.host.info." + server_name
    if host_item is None:
        host_item = HostInformation.get_or_insert(host=server_name)
    memcache.set(key=memcache_key, value=host_item, time=3600)
    namespace_manager.set_namespace(host_item.namespace)
    return host_item
