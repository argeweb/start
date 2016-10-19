"""
Classes that extend the basic ndb.Model classes
"""

from google.appengine.ext import ndb
import types
import time
from argeweb.behaviors.searchable import Searchable


class ModelMeta(ndb.model.MetaModel):
    """
    Augments Models by adding the class methods find_all_by_x
    and find_by_x that are proxies for find_all_by_properties and
    find_by_properties respectively.
    """
    def __init__(cls, name, bases, dct):
        super(ModelMeta, cls).__init__(name, bases, dct)

        # Make sure the Meta class has a proper chain
        if cls.__name__ != 'Model' and not issubclass(cls.Meta, Model.Meta):
            cls.Meta = type('Meta', (cls.Meta, Model.Meta), {})

        # Behaviors
        setattr(cls, 'behaviors', [x(cls) for x in cls.Meta.behaviors])

        # Inject finder methods
        ModelMeta._inject_find_methods(cls, name, bases, dct)

    @staticmethod
    def _inject_find_methods(cls, name, bases, dct):
        # find_by_x and find_all_by_x
        for prop_name, property in cls._properties.items():
            find_all_name = 'find_all_by_' + prop_name

            def bind_all(name):
                def find_all(cls, value):
                    args = {}
                    args[name] = value
                    return cls.find_all_by_properties(**args)
                return types.MethodType(find_all, cls)

            if not find_all_name in dct:
                setattr(cls, find_all_name, bind_all(prop_name))

            find_one_name = 'find_by_' + prop_name

            def bind_one(name):
                def find_one(cls, value):
                    args = {}
                    args[name] = value
                    return cls.find_by_properties(**args)
                return types.MethodType(find_one, cls)

            if not find_one_name in dct:
                setattr(cls, find_one_name, bind_one(prop_name))


class Model(ndb.Model):
    """
    Base class that augments ndb Models by adding easier find methods and callbacks.
    """
    __metaclass__ = ModelMeta

    class Meta(object):
        behaviors = (Searchable, )

    @classmethod
    def find_all_by_properties(cls, **kwargs):
        """
        Generates an ndb.Query with filters generated from the keyword arguments.

        Example::

            User.find_all_by_properties(first_name='Jon',role='Admin')

        is the same as::

            User.query().filter(User.first_name == 'Jon', User.role == 'Admin')

        """
        query = cls.query()
        for name, value in kwargs.items():
            property = cls._properties[name]
            query = query.filter(property == value)
        return query

    @classmethod
    def find_by_properties(cls, **kwargs):
        """
        Similar to find_all_by_properties, but returns either None or a single ndb.Model instance.

        Example::

            User.find_by_properties(first_name='Jon',role='Admin')

        """
        return cls.find_all_by_properties(**kwargs).get()

    def before_put(self):
        """
        Called before an item is saved.

        :arg self: refers to the item that is about to be saved
        :note: ``self.key`` is invalid if the current item has never been saved
        """
        pass

    def after_put(self, key):
        """
        Called after an item has been saved.

        :arg self: refers to the item that has been saved
        :arg key: refers to the key that the item was saved as
        """
        pass

    @classmethod
    def before_delete(cls, key):
        """
        Called before an item is deleted.

        :arg key: is the key of the item that is about to be deleted. It is okay to ``get()`` this key to interogate the properties of the item.
        """
        pass

    @classmethod
    def after_delete(cls, key):
        """
        Called after an item is deleted.

        :arg key: is the key of the item that was deleted. It is not possible to call ``get()`` on this key.
        """
        pass

    @classmethod
    def before_get(cls, key):
        """
        Called before an item is retrieved. Note that this does not occur for queries.

        :arg key: Is the key of the item that is to be retrieved.
        """
        pass

    @classmethod
    def after_get(cls, key, item):
        """
        Called after an item has been retrieved. Note that this does not occur for queries.

        :arg key: Is the key of the item that was retrieved.
        :arg item: Is the item itself.
        """
        pass

    # Impl details

    @classmethod
    def _invoke_behaviors(cls, method, *args, **kwargs):
        for b in cls.behaviors:
            getattr(b, method)(*args, **kwargs)

    def _pre_put_hook(self):
        self._invoke_behaviors('before_put', self)
        return self.before_put()

    def _post_put_hook(self, future):
        res = future.get_result()
        self._invoke_behaviors('after_put', self)
        return self.after_put(res)

    @classmethod
    def _pre_delete_hook(cls, key):
        cls._invoke_behaviors('before_delete', key)
        return cls.before_delete(key)

    @classmethod
    def _post_delete_hook(cls, key, future):
        cls._invoke_behaviors('after_delete', key)
        return cls.after_delete(key)

    @classmethod
    def _pre_get_hook(cls, key):
        cls._invoke_behaviors('before_get', key)
        return cls.before_get(key)

    @classmethod
    def _post_get_hook(cls, key, future):
        res = future.get_result()
        cls._invoke_behaviors('after_get', res)
        return cls.after_get(key, res)

    def __unicode__(self):
        if hasattr(self, 'name'):
            return self.name or super(Model, self).__str__()
        else:
            return super(Model, self).__str__()

    def __str__(self):
        return self.__unicode__()


class BasicModel(Model):
    """
    Adds the common properties created, created_by, modified, and modified_by to :class:`Model`
    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    #created_by = ndb.UserProperty(auto_current_user_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    #modified_by = ndb.UserProperty(auto_current_user=True)
    sort = ndb.FloatProperty(default=0.0)

    def before_put(self):
        """
        Called before an item is saved.

        :arg self: refers to the item that is about to be saved
        :note: ``self.key`` is invalid if the current item has never been saved
        """
        if self.sort is None or self.sort == 0.0:
            self.sort = time.time()
        super(BasicModel, self).before_put()

    @classmethod
    def get_prev_one(cls, item):
        return cls.query(cls.sort > item.sort).order(cls.sort).get()

    @classmethod
    def get_next_one(cls, item):
        return cls.query(cls.sort < item.sort).order(-cls.sort).get()

    @classmethod
    def get_prev_one_with_category(cls, item, cat):
        c = ndb.Key(urlsafe=cat)
        if hasattr(cls, "category"):
            return cls.query(cls.category == c, cls.sort > item.sort).order(cls.sort).get()
        else:
            return None

    @classmethod
    def get_next_one_with_category(cls, item, cat):
        c = ndb.Key(urlsafe=cat)
        if hasattr(cls, "category"):
            return cls.query(cls.category == c, cls.sort < item.sort).order(-cls.sort).get()
        else:
            return None

    @classmethod
    def all(cls):
        """
        Queries all posts in the system, regardless of user, ordered by date created descending.
        """
        return cls.query().order(-cls.sort)

    @classmethod
    def all_enable(cls, *args, **kwargs):
        if hasattr(cls, "is_enable") is False:
            return None
        if hasattr(cls, "category") and "category_key" in kwargs:
            cat = ndb.Key(urlsafe=kwargs["category_key"])
            if cat is not None:
                return cls.query(cls.category == cat.key, cls.is_enable == True).order(-cls.sort)
        else:
            return cls.query(cls.is_enable == True).order(-cls.sort)

    @classmethod
    def find_by_name(cls, name):
        if hasattr(cls, "name"):
            return cls.query(cls.name == name).get()
        else:
            return None

    @classmethod
    def find_by_title(cls, title):
        if hasattr(cls, "title"):
            return cls.query(cls.title == title).get()
        else:
            return None

    @classmethod
    def has_record(cls):
        r = cls.query().get()
        if r is not None:
            return True
        else:
            return False