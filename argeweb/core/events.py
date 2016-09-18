#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Global argeweb events.
Applications may also fire events with this bus
"""

from event import Event, NamedEvents

# The Global Events Bus
# This is just a NamedEvents object that certain parts of argeweb tap into
# to notify the application or other argeweb components about changes.
# See individual components for events.
#
# Exercise caution with threadsafety and events. You should register all
# events and listeners on application startup.
global_events = NamedEvents()


def fire(event_name, *args, **kwargs):
    """
    Calls all of the registered event handlers for a given event. Passes through all arguments
    """
    return global_events[event_name](*args, **kwargs)


def on(event_name):
    """
    Automatically called when the specified event occurs.
    """
    def inner(f):
        global_events[event_name] += f
    return inner


def register(event_or_list):
    if not isinstance(event_or_list, list):
        event_or_list = [event_or_list]
    for event in event_or_list:
        global_events.getEvent(event)

# Pre-register some events
register([
    'before_template_render',
    'after_template_render'
])


class BroadcastEvent(Event):
    def __init__(self, name=None, prefix=None):
        super(BroadcastEvent, self).__init__(name)
        self.prefix = prefix

    def fire(self, *args, **kwargs):
        results = super(BroadcastEvent, self).fire(*args, **kwargs)
        return results + fire(self.prefix + self.name, *args, **kwargs)

    __call__ = fire


class NamedBroadcastEvents(NamedEvents):
    _event_class = BroadcastEvent

    def __init__(self, prefix=None):
        super(NamedBroadcastEvents, self).__init__()
        self.prefix = prefix

    def getEventNoAttr(self, name):
        if not name in self._events:
            self._events[name] = self._event_class(name=name, prefix=self.prefix)
        return self._events[name]

    __getattr__ = getEventNoAttr


class ViewEvent(BroadcastEvent):
    def fire(self, *args, **kwargs):
        results = super(ViewEvent, self).fire(*args, **kwargs)
        return ' '.join(results)

    __call__ = fire


class ViewEvents(NamedBroadcastEvents):
    _event_class = ViewEvent
