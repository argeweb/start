"""
OAuth dance session
"""

from google.appengine.ext import ndb
from argeweb.core.ndb import Model
from oauth2client.appengine import CredentialsNDBProperty, StorageByKeyName
import hashlib


class UserCredentials(Model):

    user = ndb.UserProperty(indexed=True)
    scopes = ndb.StringProperty(repeated=True, indexed=False)
    admin = ndb.BooleanProperty(indexed=True)
    credentials = CredentialsNDBProperty(indexed=False)
    filter_scopes = ndb.ComputedProperty(lambda x: ','.join(sorted(x.scopes)), indexed=True)
    updated = ndb.DateTimeProperty(indexed=False, auto_now=True)

    def authorize(self, http):
        return self.credentials.authorize(http)

    @classmethod
    def _get_kind(cls):
        return '_argeweb_oauth2_user_credentials'

    @classmethod
    def after_get(cls, key, item):
        if item and item.credentials:
            storage = StorageByKeyName(UserCredentials, key.id(), 'credentials')
            item.credentials.set_store(storage)

    @classmethod
    def _get_key(cls, user, scopes, admin):
        scopes_hash = hashlib.sha1(','.join(sorted(scopes))).hexdigest()
        return ndb.Key(cls, '%s:%s:%s' % (user, scopes_hash, True if admin else False))

    @classmethod
    def create(cls, user, scopes, credentials, admin):
        key = cls._get_key(user, scopes, admin)
        item = cls(key=key, user=user, scopes=scopes, credentials=credentials, admin=admin)
        item.put()
        return item

    @classmethod
    def find(cls, user=None, scopes=None, admin=False):
        if user and scopes:
            key = cls._get_key(user, scopes, admin)
            x = key.get()
        else:
            q = cls.query()
            if user:
                q = q.filter(cls.user == user)
            if scopes:
                q = q.filter(cls.filter_scopes == ','.join(sorted(scopes)))
            if admin:
                q = q.filter(cls.admin == admin)
            x = q.get()

        if x:
            cls.after_get(x.key, x)
        return x

    @classmethod
    def delete_all(cls, user):
        c = cls.query().filter(user=user)
        for x in c:
            x.key.delete()


def find_credentials(user=None, scopes=None, admin=None):
    """
    Finds credentials that fit the criteria provided. If no user is provided,
    the first set of credentials that have the given scopes and privilege level.

    Returns None if no credentials are found.
    """
    return UserCredentials.find(user, scopes, admin)
