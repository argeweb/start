#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Bunch(object):
    def __init__(self, **kwds):
        self.update(kwds)

    def update(self, other):
        self.__dict__.update(other)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        return setattr(self, key, val)

    def __contains__(self, key):
        return hasattr(self, key)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __unicode__(self):
        return self.__dict__.__unicode__()

    def __str__(self):
        return self.__dict__.__str__()
