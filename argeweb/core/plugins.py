#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import argeweb
import os
from google.appengine.api import memcache

_plugins = []
_plugins_controller = []
_application_controller = []


def exists(name):
    """
    Checks to see if a particular plugin is enabled
    """
    return name in _plugins


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
    if plugin_name in _plugins:
        return
    import template
    _plugins.append(plugin_name)

    if templating:
        path = os.path.normpath(os.path.join(
            os.path.dirname(argeweb.__file__),
            '../plugins/%s/templates' % plugin_name))
        template.add_template_path(path)
        template.add_template_path(path, prefix=plugin_name)


def list():
    return _plugins


def get_plugin_controller(plugin_name):
    directory = os.path.join('plugins', plugin_name, 'controllers')
    controllers = []
    for root_path, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file not in ['__init__.py', 'settings.py']:
                controllers.append("plugins."+plugin_name+".controllers."+file.replace(".py", ""))

    if len(controllers) > 0:
        return controllers
    else:
        return ["plugins."+plugin_name+".controllers."+plugin_name]


def get_all_controller_in_application():
    return _application_controller


def set_plugins_controller(controllers):
    _plugins_controller = controllers
    return _plugins_controller


def get_all_controller_in_plugins():
    if len(_plugins_controller) > 0:
        return _plugins_controller
    plugins_controller = memcache.get('plugins.installed.all')
    if plugins_controller is not None and len(plugins_controller) > 0:
        return set_plugins_controller(plugins_controller)
    plugins_controller = []
    dir_plugins = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'plugins'))
    for dirPath in os.listdir(dir_plugins):
        if dirPath.find(".") < 0:
            plugins_controller += get_plugin_controller(dirPath)
    memcache.set('plugins.installed.all', plugins_controller)
    return plugins_controller
