#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/29.

from google.appengine.ext.ndb import GeoPtProperty, KeyProperty
from google.appengine.ext.ndb import StringProperty, BooleanProperty, IntegerProperty, FloatProperty
from google.appengine.ext.ndb import DateTimeProperty, DateProperty, TimeProperty, BlobKeyProperty, TextProperty
from argeweb.core.ndb.model import Model

__all__ = (
    'StringProperty',
    'BooleanProperty',
    'IntegerProperty',
    'FloatProperty',
    'DateTimeProperty',
    'DateProperty',
    'TimeProperty',
    'BlobKeyProperty',
    'TextProperty',
    'GeoPtProperty',
    'KeyProperty',
    'RichTextProperty',
    'CategoryProperty',
    'HiddenProperty',
    'ImageProperty',
    'ImagesProperty',
)

class ReverseReferenceProperty(list):
    pass

class RichTextProperty(TextProperty):
    __property_name__ = "richtext"


class CategoryProperty(KeyProperty):
    __property_name__ = "category"
    def _fix_up(self, cls, code_name):
        super(CategoryProperty, self)._fix_up(cls, code_name)
        modelclass = Model._kind_map[self._kind]
        collection_name = '%s_ref_%s_to_%s' % (cls.__name__,
                                               code_name,
                                               modelclass.__name__)

        setattr(modelclass, collection_name, (cls,self))


class ImageProperty(StringProperty):
    __property_name__ = "image"


class ImagesProperty(TextProperty):
    __property_name__ = "images"


class HiddenProperty(StringProperty):
    __property_name__ = "hidden"