# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from google.appengine.ext import ndb
from functools import wraps
import cPickle as pickle
import datetime
import logging
import threading
import inspect


none_sentinel_string = u'☃☸☃ - caching sentinel'


def cache(key, ttl=0, backend=None):
    """
    General-purpose caching decorator. This decorator causes the result of a function
    to be cached so that subsequent calls will return the cached result instead of
    calling the function again. The ttl argument determines how long the cache is valid,
    once the cache is invalid the function will be called to generate a new value and the
    cache will be refreshed. The backend argument can be used to determine how the value
    is cached- by default, the value is stored in memcache but there are built-in backends
    for thread-local caching and caching via the datastore.

    Example::

        @cache('something_expensive', ttl=3600)
        def expensive_function():
            ...

    """
    if backend is None or backend == 'memcache':
        backend = MemcacheBackend
    elif backend == 'local':
        backend = LocalBackend
    elif backend == 'datastore':
        backend = DatastoreBackend

    def wrapper(f):
        @wraps(f)
        def dispatcher(*args, **kwargs):
            data = backend.get(key)

            if data == none_sentinel_string:
                return None

            if data is None:
                data = f(*args, **kwargs)
                backend.set(key, none_sentinel_string if data is None else data, ttl)

            return data

        def cache_getter():
            data = backend.get(key)
            if data == none_sentinel_string:
                return None
            return data

        setattr(dispatcher, 'clear_cache', lambda: backend.delete(key))
        setattr(dispatcher, 'cached', cache_getter)
        setattr(dispatcher, 'uncached', f)
        return dispatcher
    return wrapper


def cache_by_args(key, ttl=0, backend=None):
    """
    Like :func:`cache`, but will use any arguments to the function as part of the key to
    ensure that variadic functions are cached separately. Argument must be able to be
    printed as a string- it's recommended to use plain data types as arguments.
    """
    def wrapper(f):
        argspec = inspect.getargspec(f)[0]

        if len(argspec) and argspec[0] in ('self', 'cls'):
            is_method = True
        else:
            is_method = False

        @wraps(f)
        def dispatcher(*args, **kwargs):
            targs = args if not is_method else args[1:]
            arg_key = "%s:%s:%s" % (key, targs, kwargs)

            @cache(arg_key, ttl, backend=backend)
            def inner_dispatcher():
                return f(*args, **kwargs)

            return inner_dispatcher()
        return dispatcher
    return wrapper


def cache_using_local(key, ttl=0):
    """
    Shortcut decorator for caching using the thread-local cache.
    """
    return cache(key, ttl, backend=LocalBackend)


def cache_using_memcache(key, ttl=0):
    """
    Shortcut decorator for caching using the memcache.
    """
    return cache(key, ttl, backend=MemcacheBackend)


def cache_using_datastore(key, ttl=0):
    """
    Shortcut decorator for caching using the datastore
    """
    return cache(key, ttl, backend=DatastoreBackend)


def cache_by_args_using_local(key, ttl=0):
    """
    Shortcut decorator for caching by arguments using the thread-local cache.
    """
    return cache_by_args(key, ttl, backend=LocalBackend)


def cache_by_args_using_memcache(key, ttl=0):
    """
    Shortcut decorator for caching by arguments using the memcache.
    """
    return cache_by_args(key, ttl, backend=MemcacheBackend)


def cache_by_args_using_datastore(key, ttl=0):
    """
    Shortcut decorator for caching by arguments using the datastore
    """
    return cache_by_args(key, ttl, backend=DatastoreBackend)


class LocalBackend(object):
    """
    The local backend stores caches in a thread-local variable. The caches are available
    for this thread and likely just for the duration of one request.
    """
    cache_obj = threading.local()

    @classmethod
    def set(cls, key, data, ttl):
        if ttl:
            expires = datetime.datetime.now() + datetime.timedelta(seconds=ttl)
        else:
            expires = None
        setattr(cls.cache_obj, key, (data, expires))

    @classmethod
    def get(cls, key):
        if not hasattr(cls.cache_obj, key):
            return None

        data, expires = getattr(cls.cache_obj, key)

        if expires and expires < datetime.datetime.now():
            delattr(cls.cache_obj, key)
            return None

        return data

    @classmethod
    def delete(cls, key):
        try:
            delattr(cls.cache_obj, key)
        except AttributeError:
            pass

    @classmethod
    def reset(cls):
        for a in cls.cache_obj.__dict__.keys():
            delattr(cls.cache_obj, a)


class MemcacheBackend(object):
    """
    Stores caches in memcache. Memcache is available across instances but is subject to
    being dumped from the cache before the expiration time.
    """
    @classmethod
    def set(cls, key, data, ttl):
        memcache.set(key, data, ttl)

    @classmethod
    def get(cls, key):
        return memcache.get(key)

    @classmethod
    def delete(cls, key):
        memcache.delete(key)


class MemcacheChunkedBackend(MemcacheBackend):
    """
    Stores cache in memcache as multiple chunks if needed.  Chunking code informed from
    `flask-cache` repository by Thadeus Burgess.
    """
    chunksize = 1000000 # 10^6 bytes is Memcache's max.
    # 32 Megabytes is max set_multi for memcache
    maxchunks = 32 * 1024 * 1024 // chunksize

    @classmethod
    def set(cls, key, data, ttl):
        """ Divides the object into multiple chunks and sets it. """
        serialized = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        len_serialized = len(serialized)
        # create a (generator) for chunk sizes
        chunks = xrange(0, len_serialized, cls.chunksize)
        multi_data = {}
        if len(chunks) > cls.maxchunks:
            raise ValueError("Cached object %s's size %i is %i chunks, more than maximum of %i" % \
                             (key, len_serialized, len(chunks), cls.maxchunks))

        for i in chunks:
            multi_data['%s.%i' % (key, i//cls.chunksize)] = serialized[i:i+cls.chunksize]
        return memcache.set_multi(multi_data, time=(ttl or 0))


    @classmethod
    def get(cls, key):
        """ Loads the keys from memcached and deserializes. """
        multi_keys = ['%s.%i' % (key, i) for i in xrange(cls.maxchunks)]
        multi_values = memcache.get_multi(multi_keys)
        serialized = ''.join([multi_values[k] for k in multi_keys if k in multi_values])
        if not serialized:
            return None
        return pickle.loads(serialized)

    @classmethod
    def delete(cls, key):
        """ Deletes all the keys from memcache"""
        multi_keys = ['%s.%i' % (key, i) for i in xrange(cls.maxchunks)]
        memcache.delete_multi(multi_keys)


class MemcacheCompareAndSetBackend(MemcacheBackend):
    """
    Same as the regular memcache backend but uses compare-and-set logic to ensure
    that memcache updates are atomic.
    """
    @classmethod
    def set(cls, key, data, ttl):
        client = memcache.Client()
        if not client.gets(key):
            memcache.set(key, data, ttl)
            return

        for _ in range(10):
            if client.cas(key, data, ttl):
                break


class DatastoreBackend(object):
    """
    Stores caches in the datastore which has the effect of them being durable and persistent,
    unlike the memcache and local backends. Items stored in the datastore are certain to remain
    until the expiration time passes.
    """
    @classmethod
    def set(cls, key, data, ttl):
        if ttl:
            expires = datetime.datetime.now() + datetime.timedelta(seconds=ttl)
        else:
            expires = None

        DatastoreCacheModel(id=key, data=data, expires=expires).put()

    @classmethod
    def get(cls, key):
        item = ndb.Key(DatastoreCacheModel, key).get()

        if not item:
            return None

        if item.expires and item.expires < datetime.datetime.now():
            item.key.delete()
            return None

        return item.data

    @classmethod
    def delete(cls, key):
        ndb.Key(DatastoreCacheModel, key).delete()


class DatastoreChunkedBackend(object):
    """
    Stores caches in the datastore which has the effect of them being durable and persistent,
    unlike the memcache and local backends. Items stored in the datastore are certain to remain
    until the expiration time passes.  Chunks the data if it is greater than the chunksize (1MB).
    """

    chunksize = 1024 * 1024  #1MB
    maxchunks = 20 # limit this to be close to the max obj size, to reduce number of
                   # unnecessary queries.


    @classmethod
    @ndb.toplevel
    def set(cls, key, data, ttl):
        """ Adds data to the Datastore, broken into as a series of chunks <= `chunksize`"""
        if ttl:
            expires = datetime.datetime.now() + datetime.timedelta(seconds=ttl)
        else:
            expires = None

        serialized = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        len_serialized = len(serialized)
        # create a (generator) for chunk sizes
        chunks = xrange(0, len_serialized, cls.chunksize)
        multi_data = {}
        if len(chunks) > cls.maxchunks:
            raise ValueError("Cached object %s's size %i is %i chunks, more than maxium of %i" % \
                             (key, len_serialized, len(chunks), cls.maxchunks))

        for i in chunks:
            DatastoreCacheModel(id="%s.%i" % (key, i//cls.chunksize),\
                                data=serialized[i:i+cls.chunksize],\
                                expires=expires).put_async()


    @classmethod
    def get(cls, key):
        """ Loads the key's chunks from Datastore and reassembles them. """
        multi_keys = [ndb.Key(DatastoreCacheModel, '%s.%i' % (key, i)) for i in xrange(cls.maxchunks)]
        multi_values = ndb.get_multi(multi_keys, use_memcache=False, use_cache=False)
        chunks = []
        for item in multi_values:
            if not item:
                break # end of the line
            if item.expires and item.expires < datetime.datetime.now():
                logging.info("DatastoreChunkedBackend item '%s' is expired. Returning None" % (key))
                cls.delete(key)
                return None
            chunks.append(item.data)

        serialized = ''.join(chunks)
        if not serialized:
            return None
        data = pickle.loads(serialized)
        return data

    @classmethod
    def delete(cls, key):
        """ Deletes all entires in the Datastore for the given Key's chunks."""
        multi_keys = [ndb.Key(DatastoreCacheModel, '%s.%i' % (key, i)) for i in xrange(cls.maxchunks)]
        ndb.delete_multi(multi_keys)


class DatastoreCacheModel(ndb.Model):
    data = ndb.PickleProperty(indexed=False, compressed=True)
    expires = ndb.DateTimeProperty(indexed=False)


class LayeredBackend(object):
    """
    Allows you to use multiple backends at once. When an item is cached it is put
    in to each backend. Retrieval checks each backend in order for the item. This is
    very useful when combining fast but volatile backends (like local) with slow
    but durable backends (like datastore).

    Example::

        @cache('something_expensive', ttl=3600, backend=LayeredBackend(LocalBackend, DatastoreBackend))
        def expensive_function():
            ...

    """
    def __init__(self, *args):
        self.backends = args

    def set(self, key, data, ttl):
        for b in self.backends:
            b.set(key, data, ttl)

    def get(self, key):
        for b in self.backends:
            data = b.get(key)
            if data is not None:
                return data

    def delete(self, key):
        for b in self.backends:
            b.delete(key)
