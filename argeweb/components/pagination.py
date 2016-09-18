from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.datastore.datastore_query import Cursor
import logging


class Pagination(object):
    """
    Provides a generic, reusable Pagination API.

    This can be used to automatically paginate ``ndb.Query`` objects but it can also
    be used directly to provide pagination over custom datasources.

    Automatically happens for any ``list`` actions but can also be manually invoked
    via :meth:`paginate`  or :meth:`__call__`.
    """

    def __init__(self, controller):
        self.controller = controller
        self.auto_paginate = True
        if not hasattr(self.controller.meta, 'pagination_actions'):
            setattr(self.controller.meta, 'pagination_actions', ('list',))
        self.controller.events.after_dispatch += self.after_dispatch_callback.__get__(self)

    def set_pagination_info(self, current_cursor=None, next_cursor=None, limit=None, count=None):
        """
        Sets the pagintion information for the view context. Use by your custom APIs to expose the
        next cursor, the limit, and the number of objects currently visible.

        Sets the ``paging`` template variable to a dictionary like::

            {
                "cursor": "abc...",
                "previous_cursor": "rvx...",
                "next_cursor": "nzb...",
                "limit": 10,
                "count": 10
            }
        """
        self._set_cursors(current_cursor, next_cursor)
        self.controller.context.set_dotted('paging.limit', limit)
        self.controller.context.set_dotted('paging.count', count)

    def get_pagination_info(self):
        """
        Returns the current pagination infomation from the view context: previous cursor, current cursor,
        next cursor, page, limit, and count.
        """
        ctx = self.controller.context
        return (
            ctx.get_dotted('paging.previous_cursor'),
            ctx.get_dotted('paging.cursor'),
            ctx.get_dotted('paging.next_cursor'),
            ctx.get_dotted('paging.page'),
            ctx.get_dotted('paging.limit'),
            ctx.get_dotted('paging.count'))

    def get_pagination_params(self, cursor=None, limit=None):
        """
        Retuns the pagination parameters provided by the request. Use this in your custom APIs to determine
        which cursor and the number of objects the user is requesting.
        """
        if not limit:
            limit = self.controller.meta.pagination_limit if hasattr(self.controller.meta, 'pagination_limit') else 25
        if not cursor:
            cursor = self.controller.request.params.get('cursor', None)
            if cursor == 'False':
                cursor = None
        return cursor, limit

    def _set_cursors(self, current, next):
        """
        Uses memcache to track the cursors
        """
        ctx = self.controller.context

        previous_tuple = memcache.get('paging.cursor.previous.%s' % current)

        if previous_tuple:
            page, previous = previous_tuple
        else:
            page, previous = 0, None

        page += 1

        if next:
            memcache.set('paging.cursor.previous.%s' % next, (page, current))

        logging.debug("Page: %s, Previous: %s, Current: %s, Next: %s" % (page, previous, current, next))

        ctx.set_dotted('paging.page', page)

        if previous is not None:
            ctx.set_dotted('paging.previous_cursor', previous)

        if next is not None:
            ctx.set_dotted('paging.next_cursor', next)

    def _get_query(self, name):
        if not name and hasattr(self.controller, 'scaffold'):
            name = self.controller.scaffold.plural

        if isinstance(name, basestring):
            query = self.controller.context.get(name, None)
        else:
            query = name

        if not isinstance(query, (ndb.Query,)):
            return None

        return query

    def paginate(self, query=None, cursor=None, limit=None):
        """
        Paginates a ``ndb.Query`` and sets up the appropriate template variables.

        Uses ``Controller.Meta.pagination_limit`` to determine how many items per page
        or defaults to 10 if omitted.

        Returns the data, and if ``query`` is a string, sets that template variable.

        If ``query`` is omitted it'll attempt to find the dataset using the scaffold variable names.
        """

        cursor, limit = self.get_pagination_params(cursor, limit)
        query = self._get_query(query)

        if not query:
            logging.debug('Couldn\'t auto paginate, no valid query found')
            return

        if cursor and not isinstance(cursor, Cursor):
            cursor = Cursor(urlsafe=cursor)

        if cursor is u"":
            cursor = None
        data, next_cursor, more = query.fetch_page(limit, start_cursor=cursor)

        if hasattr(self.controller, 'scaffold'):
            self.controller.context[self.controller.scaffold.plural] = data
        else:
            logging.debug('Could not set data')

        self.set_pagination_info(
            current_cursor=cursor.urlsafe() if cursor else False,
            next_cursor=next_cursor.urlsafe() if more else False,
            limit=limit,
            count=len(data)
        )

        return data

    __call__ = paginate

    def after_dispatch_callback(self, response, *args, **kwargs):
        if self.controller.route.action in self.controller.meta.pagination_actions and self.auto_paginate:  # checks for list and any prefixed lists
            self()
