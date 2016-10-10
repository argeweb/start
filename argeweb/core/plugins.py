#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import argeweb
import os
from settings import HostInformationModel, update_memcache
from google.appengine.api import namespace_manager
from google.appengine.api import memcache

_plugin_enable_list = []
_plugins_controller = []
_application_controller = []


def get_enable_list():
    return _plugin_enable_list


def exists(name):
    """
    Checks to see if a particular plugin is enabled
    """
    return name in _plugin_enable_list


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
    Adds a plugin's template path to the templating engine
    """
    if plugin_name in _plugin_enable_list:
        return
    import template
    _plugin_enable_list.append(plugin_name)

    if templating:
        path = os.path.normpath(os.path.join(
            os.path.dirname(argeweb.__file__),
            '../plugins/%s/templates' % plugin_name))
        template.add_template_path(path)
        template.add_template_path(path, prefix=plugin_name)


def get_plugin_controller(plugin_name):
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


def get_prohibited_controller():
    return set(get_all_controller()) - set(get_enable_list())


def get_all_controller():
    return get_all_controller_in_application() + get_all_controller_in_plugins()


def get_all_controller_in_application():
    # if len(_application_controller) > 0:
    #     return _application_controller
    # application_controller = memcache.get('application.all.controller')
    # if application_controller is not None and len(application_controller) > 0:
    #     return application_controller
    application_controller = []

    base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    has_controllers_dir = True
    directory = os.path.join('application', 'controllers')
    if os.path.exists(directory) is False:
        has_controllers_dir = False
        directory = os.path.join('application')

    directory = os.path.join(base_directory, directory)
    # base_directory_path_len = len(base_directory.split(os.path.sep))

    if not os.path.exists(directory):
        return

    # walk the app/controllers directory and sub-directories
    for root_path, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".py") == False or file_name in ['__init__.py', 'settings.py']:
                continue
            controller_name = file_name.split('.')[0]
            register_application_controller(controller_name)
            if has_controllers_dir:
                application_controller.append("application.controllers.%s" % controller_name)
    return application_controller


def get_all_controller_in_plugins():
    if len(_plugins_controller) > 0:
        return _plugins_controller
    plugins_controller = memcache.get('plugins.all.controller')
    if plugins_controller is not None and len(plugins_controller) > 0:
        return plugins_controller
    plugins_controller = []
    dir_plugins = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'plugins'))
    for dirPath in os.listdir(dir_plugins):
        if dirPath.find(".") < 0:
            plugins_controller += get_plugin_controller(dirPath)
    memcache.set('plugins.all.controller', plugins_controller, 60)
    return plugins_controller


def get_enable_plugins_from_db(server_name, namespace):
    namespace_manager.set_namespace("shared")
    host_item = HostInformationModel.get_by_host(server_name)
    namespace_manager.set_namespace(namespace)
    return str(host_item.plugins).split(",")


def set_enable_plugins_to_db(server_name, namespace, plugins):
    namespace_manager.set_namespace("shared")
    host_item = HostInformationModel.get_by_host(server_name)
    host_item.plugins = ",".join(plugins)
    host_item.put()
    update_memcache(server_name, host_item)
    namespace_manager.set_namespace(namespace)