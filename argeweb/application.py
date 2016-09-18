#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/6/14.
import os
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
use_error_handlers = True
_instance = None
_setting = None

def get_setting():
    from argeweb.core import settings
    settings.load_settings()
    return settings, settings.settings()
 
def get_instance(application_path=None):
    global _instance
    if _instance is not None:
        return _instance
    from webapp2 import WSGIApplication
    from argeweb.core import errors
    from argeweb.core import routing
    settings, s = get_setting()
 
    appstats_settings = s['appstats']
    app_config_settings = s['app_config']
 
    _instance = WSGIApplication(
        debug=debug, config=app_config_settings)
 
    # Custom Error Handlers
    _instance.error_handlers[400] = errors.handle_400
    _instance.error_handlers[401] = errors.handle_401
    _instance.error_handlers[403] = errors.handle_403
    _instance.error_handlers[404] = errors.handle_404
    _instance.error_handlers[500] = errors.handle_500

    routing.auto_route(_instance.router, application_path, debug)
 
    if (appstats_settings.get('enabled', False) and debug) or appstats_settings.get('enabled_live', True):
        from google.appengine.ext.appstats import recording
        _instance = recording.appstats_wsgi_middleware(_instance)
    return _instance
 
instance = get_instance()