#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import argeweb
import os
from caching import cache
from model import HostInformationModel
from settings import update_memcache
from google.appengine.api import namespace_manager
from google.appengine.api import memcache

_plugin_installed_list = []
_plugins_controller = []
_application_controller = []


def get_installed_list():
    return _plugin_installed_list


def exists(name):
    """
    Checks to see if a particular plugin is enabled
    """
    return name in _plugin_installed_list


def register_plugin_controller(controller_name):
    if controller_name in _plugins_controller:
        return
    _plugins_controller.append(controller_name)


def register_application_controller(controller_name):
    if controller_name in _application_controller:
        return
    _application_controller.append(controller_name)


def register_template(plugin_name, templating=True):
    """
        將 plugin 的樣版目錄加至樣版列表
        """
    if plugin_name in _plugin_installed_list:
        return
    import template
    _plugin_installed_list.append(plugin_name)

    if templating:
        path = os.path.normpath(os.path.join(
            os.path.dirname(argeweb.__file__),
            '../plugins/%s/templates' % plugin_name))
        template.add_template_path(path)
        template.add_template_path(path, prefix=plugin_name)


def get_prohibited_controllers(server_name, namespace):
    """
        取得沒有被啟用的 plugin 下
        """
    a = set(get_all_controller_in_plugins())
    b = []

    for plugin in get_enable_plugins_from_db(server_name, namespace):
        for item in get_controller_in_plugin(plugin):
            b.append(item)
    return a - set(b)


def get_helper(plugin_name_or_controller):
    if plugin_name_or_controller is None:
        return None
    if isinstance(plugin_name_or_controller, basestring) is True:
        plugin_name = plugin_name_or_controller
    else:
        controller_module_name = str(plugin_name_or_controller.__module__)
        try:
            if controller_module_name.startswith('plugins'):
                plugin_name = controller_module_name.split(".")[1]
            else:
                return None
        except:
            return None
    try:
        module = __import__('plugins.%s' % plugin_name, fromlist=['*'])
        return getattr(module, "plugins_helper")
    except AttributeError:
        logging.debug("%s's plugin helper not found" % plugin_name)
        return None
    except ImportError:
        logging.debug("%s's plugin helper not found" % plugin_name)
        return None


def get_all_plugin(use_cache=True):
    """
        取得所有的 controller
        """
    c = get_all_controller_in_plugins(use_cache)
    b = [item.split(".")[1] if item.find(".") > 0 else item for item in c]
    c = list(set(b))
    c.sort(key=b.index)
    return c


@cache("get_all_controller")
def get_all_controller():
    """
        取得所有的 controller
        """
    return get_all_controller_in_application() + get_all_controller_in_plugins()


@cache("get_all_controller_in_application")
def get_all_controller_in_application():
    """
        取得 Application 目錄下所有的 controller
        """
    application_controller = []
    base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    has_controllers_dir = True
    directory = os.path.join('application', 'controllers')
    if os.path.exists(directory) is False:
        has_controllers_dir = False
        directory = os.path.join('application')
    directory = os.path.join(base_directory, directory)
    if not os.path.exists(directory):
        return
    for root_path, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".py") == False or file_name in ['__init__.py', 'settings.py']:
                continue
            controller_name = file_name.split('.')[0]
            register_application_controller(controller_name)
            if has_controllers_dir:
                application_controller.append("application.controllers.%s" % controller_name)
    return application_controller


def get_controller_in_plugin(plugin_name):
    """
        取得特定 plugin 目錄下所有的 controller
        """
    directory = os.path.join('plugins', plugin_name, 'controllers')
    controllers = []
    for root_path, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".py") and file_name not in ['__init__.py', 'settings.py']:
                controllers.append("plugins."+plugin_name+".controllers."+file_name.replace(".py", ""))
    register_plugin_controller(plugin_name)
    if len(controllers) > 0:
        return controllers
    else:
        return ["plugins."+plugin_name+".controllers."+plugin_name]


@cache("get_all_controller_in_plugins")
def get_all_controller_in_plugins(use_cache=True):
    """
        取得 plugins 下所有的 controller
        """
    if use_cache is True:
        plugins_controller = memcache.get('plugins.all.controller')
        if plugins_controller is not None and len(plugins_controller) > 0:
            return plugins_controller
    plugins_controller = []
    dir_plugins = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'plugins'))
    for dirPath in os.listdir(dir_plugins):
        if dirPath.find(".") < 0:
            plugins_controller += get_controller_in_plugin(dirPath)
    memcache.set(key='plugins.all.controller', value=plugins_controller, time=60)
    return plugins_controller


def get_enable_plugins_from_db(server_name, namespace):
    """
        取得 HostInformation 裡的 Plugins ( 取得已啟用的 Plugin )
        """
    namespace_manager.set_namespace("shared")
    host_item = HostInformationModel.get_by_host(server_name)
    namespace_manager.set_namespace(namespace)
    return str(host_item.plugins).split(",")


def set_enable_plugins_to_db(server_name, namespace, plugins):
    """
        設定 HostInformation 裡的 Plugins ( 設定啟用的 Plugin )
        """
    namespace_manager.set_namespace("shared")
    host_item = HostInformationModel.get_by_host(server_name)
    host_item.plugins = ",".join(plugins)
    host_item.put()
    update_memcache(server_name, host_item)
    namespace_manager.set_namespace(namespace)