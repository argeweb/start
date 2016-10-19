#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2014/9/30
import os
import logging
import inspect
from . import events
from .model import HostInformationModel, WebSettingModel
from google.appengine.api import namespace_manager
from google.appengine.api import memcache

_defaults = {}


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
            host_item = HostInformationModel.get_by_host(host)
            if host_item is not None:
                return_string = getattr(host_item, key)
                memcache.set(key=memcache_key, value=return_string, time=timeout)
    return return_string, host_item


def get_theme(server_name, namespace):
    namespace_manager.set_namespace("shared")
    host_item = HostInformationModel.get_by_host(server_name)
    namespace_manager.set_namespace(namespace)
    return host_item.theme


def set_theme(server_name, namespace, theme):
    namespace_manager.set_namespace("shared")
    host_item = HostInformationModel.get_by_host(server_name)
    host_item.theme = theme
    host_item.put()
    update_memcache(server_name, host_item)
    namespace_manager.set_namespace(namespace)


def get_host_information_item(server_name):
    namespace_manager.set_namespace("shared")
    memcache_key = "host.information." + server_name
    host_item = memcache.get(memcache_key)
    if host_item is None:
        host_item = HostInformationModel.get_or_insert(
            host=server_name,
            theme="install",
            plugins="application_user,application_user_role,backend_ui_material,scaffold,themes,web_file,web_page,web_setting,webdav,plugin_manager",
            is_lock=True
        )
        host_item = update_memcache(server_name, host_item)
    host_item.plugin_enable_list = str(host_item.plugins).split(",")
    host_item.application_controller_list = []
    return host_item, host_item.namespace, host_item.theme


def update_memcache(server_name, host_item=None):
    namespace_manager.set_namespace("shared")
    memcache_key = "host.information." + server_name
    memcache.set(key=memcache_key, value=host_item, time=3600)
    namespace_manager.set_namespace(host_item.namespace)
    return host_item
