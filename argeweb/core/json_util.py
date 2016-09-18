#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provides methods for serializing App Engine Datastore classes
"""

import calendar
import datetime
import time

from google.appengine.api import users
from google.appengine.ext import db, ndb, blobstore
from google.appengine.datastore import entity_pb
import json


def parse(str):
    return json.loads(str, cls=DatastoreDecoder)


def stringify(data):
    return json.dumps(data, cls=DatastoreEncoder)


class DatastoreEncoder(json.JSONEncoder):
    """
    Extends JSONEncoder to add support for App Engine Datastore Objects.

    db.Key is encoded as:
    {
        '__class__': 'db.Key',
        '__key__': 'azK...',
        '__id___': '200'
    }

    db.Model is encoded as:
    {
        '__class__': 'db.Model'
        '__key__': 'azK...',
        '__id__': '200',
        'name': 'Jon',
        'location': {
            'key': 'azB..'
            ...
        }
    }

    db.Query is encoded as an array of db.Models

    datetime is encoded in pieces.

    User is encoded as:
    {
        'nickname': 'Jon Wayne',
        'email': 'jonathan.parrott@cloudsherpas.com',
        'user_id': 12345523453
    }
    """

    def default(self, obj):
        if hasattr(obj, '__json__'):
            return getattr(obj, '__json__')()

        elif isinstance(obj, blobstore.BlobKey):
            return {'__class__': 'blobstore.BlobKey', '__key__': str(obj)}

        elif isinstance(obj, (db.Query, ndb.Query)):
            return list(obj)

        elif isinstance(obj, db.Key):
            return {'__class__': 'db.Key', '__kind__': obj.kind(), '__id__': obj.id(), '__key__': str(obj)}

        elif isinstance(obj, ndb.Key):
            return {'__class__': 'ndb.Key', '__kind__': obj.kind(), '__id__': obj.id(), '__key__': obj.urlsafe()}

        elif isinstance(obj, ndb.GeoPt):
            return {'__class__': 'ndb.GeoPt', 'lat': obj.lat, 'lon': obj.lon}

        elif isinstance(obj, db.Model):
            properties = obj.properties().items()
            output = {'__class__': 'db.Model', '__kind__': obj.__class__.kind(), '__key__': None, '__id__': None}
            if obj.is_saved():
                output.update({'__id__': obj.key().id(), '__key__': str(obj.key())})

            for field, value in properties:
                if isinstance(value, db.BlobProperty):
                    continue
                output[field] = getattr(obj, field)
            return output

        elif isinstance(obj, ndb.Model):
            output = {'__class__': 'ndb.Model', '__kind__': obj.__class__._get_kind(), '__key__': None, '__id__': None}
            if obj.key:
                output.update({'__id__': obj.key.id(), '__key__': obj.key.urlsafe()})

            def create_output(name, prop, output):
                try:
                    if isinstance(prop, ndb.BlobProperty) and not isinstance(prop, (ndb.StringProperty, ndb.TextProperty)):
                        return
                    output[name] = getattr(obj, name)
                except AttributeError:
                    pass  # We got an bad property (old, etc.)

            if obj._projection:
                for name in obj._projection:
                    create_output(name, obj._properties[name], output)
            else:
                for name, prop in obj._properties.items():
                    create_output(name, prop, output)
            return output

        elif isinstance(obj, datetime.time):
            return {
                '__class__': 'Time',
                'hour': obj.hour,
                'minute': obj.minute,
                'second': obj.second,
                'microsecond': obj.microsecond,
                'isoformat': obj.isoformat(),
            }

        elif isinstance(obj, datetime.datetime):
            output = {'__class__': 'Datetime'}
            fields = ['day', 'hour', 'microsecond', 'minute', 'month', 'second', 'year']
            methods = ['isoformat', 'timetuple']
            for field in fields:
                output[field] = getattr(obj, field)
            for method in methods:
                output[method] = getattr(obj, method)()
            output['timestamp'] = calendar.timegm(obj.utctimetuple())
            return output

        elif isinstance(obj, datetime.date):
            return {
                '__class__': 'Date',
                'day': obj.day,
                'month': obj.month,
                'year': obj.year,
                'isoformat': obj.isoformat()
            }

        elif isinstance(obj, time.struct_time):
            return list(obj)

        elif isinstance(obj, users.User):
            output = {'__class__': 'User'}
            methods = ['nickname', 'email', 'user_id']
            for method in methods:
                output[method] = getattr(obj, method)()
            return output

        try:
            result = json.JSONEncoder.default(self, obj)
            return result
        except TypeError:
            return str(obj)


class DatastoreDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        if 'object_hook' not in kwargs:
            kwargs['object_hook'] = self.object_hook

        super(DatastoreDecoder, self).__init__(*args, **kwargs)

    def object_hook(self, dict):
        if '__class__' in dict:
            classname = dict['__class__']
            if classname == 'User':
                return self.decode_user_object(dict)
            elif classname == 'Date':
                return self.decode_date_object(dict)
            elif classname == 'Time':
                return self.decode_time_object(dict)
            elif classname == 'Datetime':
                return self.decode_datetime_object(dict)
            elif classname == 'ndb.Key':
                return self.decode_ndb_key_object(dict)
            elif classname == 'ndb.GeoPt':
                return self.decode_ndb_geopt_object(dict)
            elif classname == 'ndb.Model':
                return self.decode_ndb_model_object(dict)
            elif classname == 'blobstore.BlobKey':
                return self.decode_blobkey_object(dict)
        return dict

    def decode_user_object(self, dict):
        return users.User(email=dict['email'])

    def decode_date_object(self, dict):
        return datetime.date(dict['year'], dict['month'], dict['day'])

    def decode_time_object(self, dict):
        return datetime.time(dict['hour'], dict['minute'], dict['second'], dict['microsecond'])

    def decode_datetime_object(self, dict):
        return datetime.datetime.utcfromtimestamp(dict['timestamp'])

    def decode_ndb_key_object(self, dict):
        return ndb.Key(urlsafe=dict['__key__'])

    def decode_ndb_geopt_object(self, dict):
        return ndb.GeoPt(dict['lat'], dict['lon'])

    def decode_ndb_model_object(self, dict):
        key = dict['__key__']
        kind = dict['__kind__']

        if not kind in ndb.Model._kind_map:
            return dict

        kind_class = ndb.Model._kind_map[kind]

        if key:
            key = ndb.Key(urlsafe=key)

        property_values = {k: dict[k] for k, v in kind_class._properties.iteritems() if k in dict}

        ins = kind_class(key=key, **property_values)
        return ins

    def decode_blobkey_object(self, dict):
        return blobstore.BlobKey(dict['__key__'])
