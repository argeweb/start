#!/usr/bin/env python
# -*- coding: utf-8 -*-
import webapp2
import routing
from google.appengine.api import namespace_manager


# Sentinel for the uri methods.
route_sentinel = object()


class Uri(object):
    """
    URI Utility class to help controllers and anything else
    that deals with URIs
    """

    def get_route_name(self,
                       prefix=route_sentinel,
                       controller=route_sentinel,
                       action=route_sentinel):
        """
        Function used to build the route name for a given prefix, controller, and
        action. For example, build_action_route('admin','pages','view', id=2)
        will give you "admin:pages:view". Set prefix to False to exclude the
        current prefix from the route name.
        """
        prefix = prefix if prefix != route_sentinel else self.route.prefix
        controller = controller if controller != route_sentinel else self.route.controller
        action = action if action != route_sentinel else self.route.action

        return routing.name_from_canonical_parts(prefix, controller, action)

    def uri(self, route_name=None,
            prefix=route_sentinel,
            controller=route_sentinel,
            action=route_sentinel,
            _pass_all=False,
            *args, **kwargs):
        """
        Generate in-application URIs (or URLs).

        :param route_name: The route name for which to generate a URI for, if not provided then prefix, controller, and action will be used to determine the route name
        :param prefix: The prefix of the desired URI, if omitted then the current prefix is used.
        :param controller: The controller name of the desired URI, if omitted then the current controller is used.
        :param action: The action name of the desired URI, if omitted then the current action is used.
        :param _pass_all: will pass all current URI parameters to the generated URI (useful for pagination, etc.)
        :param _full: generate a full URI, including the hostname.
        :param kwargs: arguments passed at URL or GET parameters.

        Examples::

            uri('foxes:run') # -> /foxes/run
            uri(prefix=False, controller='foxes', action='run')  # -> /foxes/run

            # when currently at /foxes/run
            uri(action='hide') # -> /foxes/hide

        """
        if not route_name:
            route_name = self.get_route_name(prefix, controller, action)

        if _pass_all:
            tkwargs = dict(self.request.route_kwargs)

            targs = tuple(self.request.route_args)
            targs = args + targs

            gargs = dict(self.request.GET)
            tkwargs.update(gargs)
            tkwargs.update(kwargs)
        else:
            tkwargs = kwargs

        tkwargs = {key: value for key, value in tkwargs.items()
                   if value is not None}
        for key, value in tkwargs.items():
            if isinstance(value, unicode):
                tkwargs[key] = value.encode("utf-8")

        return webapp2.uri_for(route_name, *args, **tkwargs)

    def uri_action_link(self, action, item=None, *varargs, **kwargs):
        if item is None:
            return self.uri(action=action, *varargs, **kwargs)
        else:
            return self.uri(action=action, key=item.key.urlsafe(), *varargs, **kwargs)

    def uri_exists(self, route_name=None,
                   prefix=route_sentinel,
                   controller=route_sentinel,
                   action=route_sentinel,
                   *args, **kwargs):
        """
        Check if a route exists.
        """
        if not route_name:
            route_name = self.get_route_name(prefix, controller, action)

        return routing.route_name_exists(route_name), route_name

    def uri_exists_with_permission(self, route_name=None, *args, **kwargs):
        if "namespace" in kwargs:
            namespace_manager.set_namespace(kwargs["namespace"])
        if "item" in kwargs:
            item = kwargs["item"]
            try:
                self.uri(route_name, key=self.util.encode_key(item))
                returnVal = True
                return_name = route_name
            except:
                returnVal = False
                return_name = route_name
        else:
            returnVal, return_name = self.uri_exists(route_name=route_name, *args, **kwargs)
        if returnVal and return_name not in self.prohibited_actions:
            return True
        else:
            return False

    def on_uri(self, route_name=None,
               prefix=route_sentinel,
               controller=route_sentinel,
               action=route_sentinel,
               **kwargs):
        """
        Checks to see if we're currently on the specified route.
        """
        if not route_name:
            route_name = self.get_route_name(prefix, controller, action)
        if route_name == routing.current_route_name():
            route_matches = True
        else:
            route_matches = False

        if not kwargs or not route_matches:
            return route_matches

        for name, value in kwargs.items():
            if not self.request.params.get(name, None) == value and not self.request.route_kwargs.get(name, None) == value:
                return False

        return True
