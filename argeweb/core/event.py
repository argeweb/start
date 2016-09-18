#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
argeweb event class
"""

import logging
import bisect


class Event(object):
    """
    Provides a simple interface for slot/signal event system.
    Example:

        myevent = Event()
        myevent += some_handler_function
        myevent()
    """
    def __init__(self, name=None):
        self.handlers = []
        self.name = name

    def handle(self, handler, priority=0):
        """
        Add a handler function to this event. You can also use +=
        """
        if not (priority, handler) in self.handlers:
            bisect.insort(self.handlers, (priority, handler))
        return self

    def unhandle(self, handler, priority=0):
        """
        Remove a handler function from this event. If it's not in the
        list, it'll raise a ValueError.
        """
        try:
            self.handlers.remove((priority, handler))
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        """
        Trigger all of the event handlers for this event. Arguments
        are passed through. You can also use self().
        """
        #logging.debug('Event %s firing %s listeners' % (self.name, self.handlers))
        results = []
        for p, handler in self.handlers:
            results.append(handler(*args, **kargs))
        return results

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__ = getHandlerCount


class NamedEvents(object):
    """
    A simple container of events.

    Example:
        events = NamedEvents()
        events.myevent += somefunction()
        events.myevent.fire()
    """
    def __init__(self):
        self._events = {}

    def getEvent(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        return self.getEventNoAttr(name)

    def getEventNoAttr(self, name):
        if not name in self._events:
            self._events[name] = Event(name=name)
        return self._events[name]

    def setEventNoAttr(self, name, value):
        if not isinstance(value, Event):
            object.__setattr__(self, name, value)
        self._events[name] = value

    def setEvent(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
        self.setEventNoAttr(name, value)

    def clear(self):
        self._events.clear()

    __getitem__ = getEvent
    __setitem__ = setEvent
    __getattr__ = getEventNoAttr
    __setattr__ = setEventNoAttr
