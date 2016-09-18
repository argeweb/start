import functools


class EdgeCache(object):
    """
    Provides easy methods to for setting edge caching, both via the browser and App Engine's
    intermediate caching proxies.
    """

    def __init__(self, controller):
        self.controller = controller

    def _get_default_expiration(self):
        return self.controller.meta.default_cache_expiration if hasattr(self.controller.meta, 'default_cache_expiration') else 15

    def set(self, mode='public', minutes=None):
        if minutes is None:
            minutes = self._get_default_expiration()

        self.controller.response.cache_control.no_cache = None
        self.controller.response.cache_control.max_age = 60 * minutes

        if mode == 'public':
            self.controller.response.cache_control.public = True
        else:
            self.controller.response.cache_control.private = True

    __call__ = set


def set(mode='public', minutes=None):
    """
    Decorator that calls the cache component automatically for an action
    """
    def inner(f):
        @functools.wraps(f)
        def inner2(self, *args, **kwargs):
            self.components.edge_cache(mode, minutes)
            return f(self, *args, **kwargs)
        return inner2
    return inner
