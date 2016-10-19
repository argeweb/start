#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
argeweb' routing utilities
"""

import os
import inspect
import webapp2
import logging
import argeweb
import inflector
from webapp2 import Route
from webapp2_extras import routes
import plugins_information


def get_true_name_and_argspec(method):
    """
    Drills through layers of decorators attempting to locate
    the actual argspec for the method.
    """

    argspec = inspect.getargspec(method)
    args = argspec[0]
    if args and args[0] == 'self':
        return method.__name__, argspec
    if hasattr(method, '__func__'):
        method = method.__func__
    if not hasattr(method, 'func_closure') or method.func_closure is None:
        raise Exception("No closure for method.")

    method = method.func_closure[0].cell_contents
    return get_true_name_and_argspec(method)


def router():
    from argeweb import app
    return app.app.router


def add(route, app_router=None):
    """
    Adds a webapp2.Route class to the router
    """
    if not app_router:
        app_router = router()
    app_router.add(route)


def auto_route(app_router, debug=True):
    """
    Automatically routes all controllers in main app and plugins
    """
    for item in plugins_information.get_all_controller():
        try:
            route_controllers(app_router, item)
        except ImportError, e:
            if debug:
                logging.error("Plugin %s does not exist, or contains a bad import: %s" % (item, e))
                raise
            else:
                pass


def redirect(url, to, app_router=None):
    """
    Adds a redirect route with the given url templates.
    """
    add(routes.RedirectRoute(url, redirect_to=to), app_router)


def route_controllers(app_router, controller_path=None):
    """
    Called in app.routes to automatically route all controllers in the app/controllers
    folder
    """
    sp = ("%s" % controller_path).split(".")
    type_name = sp[0]
    controller_name = sp[-1]
    try:
        module = __import__('%s' % controller_path, fromlist=['*'])
        try:
            cls = getattr(module, inflector.camelize(controller_name))
            route_controller(cls, app_router)
            if type_name == "plugins":
                plugins_information.register_template(controller_name)
        except AttributeError:
            logging.debug("Controller %s not found, skipping" % inflector.camelize(controller_name))
    except ImportError as e:
        logging.error('Thought %s was a controller, but was wrong (or ran into some weird error): %s' % (controller_name, e))
    except AttributeError as e:
        logging.error('Thought %s was a controller, but was wrong (or ran into some weird error): %s' % (controller_name, e))
        raise


def route_controller(controller_cls, app_router=None):
    """
    Adds all of the routes for the given controller
    """
    if not app_router:
        app_router = router()
    return controller_cls._build_routes(app_router)


def route_name_exists(name, *args, **kwargs):
    """
    Checks if a particlar named route (i.e. 'entries-list') exists.
    """
    route = webapp2.get_app().router.build_routes.get(name)
    return True if route else False


def current_route_name():
    """
    Gets the name (i.e. 'entries-list') from the router.
    """
    name = webapp2.get_app().request.route.name
    return name


def canonical_parts_from_method(controller, method):
    """
    Returns the canonical parts (prefix, controller, action, named arguments)
    from a controller's method
    """
    method_name, method_args = get_true_name_and_argspec(method)
    method_class = controller
    method_class_name = inflector.underscore(method_class.__name__)
    prefix = None

    if hasattr(method_class, 'Meta'):
        prefixes = method_class.Meta.prefixes
    else:
        prefixes = method_class.prefixes

    for tprefix in prefixes:
        if method_name.startswith(tprefix + '_'):
            prefix = tprefix
            method_name = method_name.replace(prefix + '_', '')

    return {
        'prefix': prefix,
        'controller': method_class_name,
        'action': method_name,
        'args': method_args.args[1:]  # exclude self
    }


def path_from_canonical_parts(prefix, controller, action, args):
    """
    Returns a route ('/admin/users/edit/3') from canonical parts
    ('admin', 'users', 'edit', [id])
    """
    args_parts = ['<' + x + '>' for x in args]
    route_parts = [prefix, controller, action] + args_parts
    route_parts = [x for x in route_parts if x]
    route_path = '/' + '/'.join(route_parts)

    return route_path


def name_from_canonical_parts(prefix, controller, action, args=None):
    """
    Returns the route's name ('admin-users-edit') from the canonical
    parts ('admin','users','edit')
    """
    route_parts = [prefix, controller, action]
    route_parts = [x for x in route_parts if x]
    route_name = ':'.join(route_parts)

    return route_name


def build_routes_for_controller(controllercls):
    """
    Returns list of routes for a particular controller, to enable
    methods to be routed, add the argeweb.core.controller.auto_route
    decorator, or simply set the 'route' attr of the function to
    True.

    def some_method(self, arg1, arg2, arg3)

    becomes

    /controller/some_method/<arg1>/<arg2>/<arg3>
    """
    routes_list = []
    name_counters = {}

    for entry in controllercls._route_list:
        method = entry[0]
        args = entry[1]
        kwargs = entry[2]

        parts = canonical_parts_from_method(controllercls, method)
        route_path = path_from_canonical_parts(**parts)
        route_name = name_from_canonical_parts(**parts)

        # not the most elegant way to determine the
        # correct member name, but it works. Alternatively,
        # i could use get_real_name_and_argspect, but
        # cononical_parts_from_method already does that.
        method = parts['action']

        if parts['prefix']:
            method = '%s_%s' % (parts['prefix'], parts['action'])

        name_counters[route_name] = name_counters.get(route_name, 0) + 1
        if name_counters[route_name] > 1:
            route_name = '%s-%d' % (route_name, name_counters[route_name])

        tkwargs = dict(
            template=route_path,
            handler=controllercls,
            name=route_name,
            handler_method=method
        )

        tkwargs.update(kwargs)
        # ingest args[0] if its the only thing set
        if len(args) == 1:
            tkwargs['template'] = args[0]
        if len(args) > 1:
            raise ValueError("Only one positional argument may be passed to route_with")

        routes_list.append(Route(**tkwargs))

    return routes_list


def build_scaffold_routes_for_controller(controllercls, prefix_name=None):
    """
    Automatically sets up a restful routing interface for a controller
    that has any of the rest methods (list, view, add, edit, delete)
    either without or with a prefix. Note that these aren't true rest
    routes, some more wizardry has to be done for that.

    The routes generated are:

    controller:list : /controller
    controller:view : /controller/:id
    controller:add  : /controller/add
    controller:edit : /controller/:id/edit
    controller:delete : /controller/:id/delete

    prefixes just add to the beginning of the name and uri, for example:

    admin:controller:edit: /admin/controller/:id/edit
    """
    if(hasattr(controllercls, 'name')):
        name = controllercls.name
    name = inflector.underscore(controllercls.__name__)
    prefix_string = ''

    if prefix_name:
        prefix_string = prefix_name + '_'

    top = []
    path = []
    id = []

    # GET /controller -> controller::list
    method_name = prefix_string + 'list'
    if hasattr(controllercls, method_name):
        top.append(Route('/' + name, controllercls, 'list', handler_method=method_name, methods=['HEAD', 'GET']))

    # GET /controller/:urlsafe -> controller::view
    if hasattr(controllercls, prefix_string + 'view'):
        path.append(Route('/:<key>', controllercls, 'view', handler_method=prefix_string + 'view', methods=['HEAD', 'GET']))

    # GET/POST /controller/add -> controller::add
    # POST /controller -> controller::add
    if hasattr(controllercls, prefix_string + 'add'):
        path.append(Route('/add', controllercls, 'add', handler_method=prefix_string + 'add', methods=['GET', 'POST']))
        top.append(Route('/' + name, controllercls, 'add:rest', handler_method=prefix_string + 'add', methods=['POST']))

    # GET/POST /controller/:urlsafe/edit -> controller::edit
    # PUT /controller/:urlsafe -> controller::edit
    if hasattr(controllercls, prefix_string + 'edit'):
        id.append(Route('/edit', controllercls, 'edit', handler_method=prefix_string + 'edit', methods=['GET', 'POST']))
        path.append(Route('/:<key>', controllercls, 'edit:rest', handler_method=prefix_string + 'edit', methods=['PUT', 'POST']))

    # GET /controller/:urlsafe/delete -> controller::delete
    # DELETE /controller/:urlsafe -> controller::d
    if hasattr(controllercls, prefix_string + 'delete'):
        id.append(Route('/delete', controllercls, 'delete', handler_method=prefix_string + 'delete'))
        path.append(Route('/:<key>', controllercls, 'delete:rest', handler_method=prefix_string + 'delete', methods=["DELETE"]))

    if hasattr(controllercls, prefix_string + 'sort_up'):
        id.append(Route('/sort_up', controllercls, 'sort_up', handler_method=prefix_string + 'sort_up'))

    if hasattr(controllercls, prefix_string + 'sort_down'):
        id.append(Route('/sort_down', controllercls, 'sort_down', handler_method=prefix_string + 'sort_down'))

    if hasattr(controllercls, prefix_string + 'set_boolean_field'):
        id.append(Route('/set_boolean_field', controllercls, 'set_boolean_field', handler_method=prefix_string + 'set_boolean_field'))

    if hasattr(controllercls, prefix_string + 'plugins_check'):
        id.append(Route('/plugins_check', controllercls, 'plugins_check', handler_method=prefix_string + 'plugins_check'))

    top_route = routes.NamePrefixRoute(name + ':', top + [
        routes.PathPrefixRoute('/' + name, path + [
            routes.PathPrefixRoute('/:<key>', id)
        ])
    ])

    if prefix_name:
        prefix_route = routes.NamePrefixRoute(prefix_name + ':', [
            routes.PathPrefixRoute('/' + prefix_name, [top_route])
        ])
        return prefix_route

    return top_route
