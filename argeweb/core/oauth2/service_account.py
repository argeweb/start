from google.appengine.ext import ndb
import hashlib
import logging


def get_config():
    from argeweb import settings
    config = settings.get('oauth2_service_account')
    if not config['private_key'] or not config['client_email']:
        raise RuntimeError("OAuth2 Service Account is not configured correctly")
    return config


try:
    from oauth2client.client import SignedJwtAssertionCredentials
except ImportError:
    logging.critical("PyCrypto is not available and the OAuth2 service account will not work. Please install PyCrypto to remove this warning.")
    SignedJwtAssertionCredentials = None

from oauth2client.appengine import StorageByKeyName, CredentialsNDBProperty


def build_credentials(scope, user=None):
    """
    Builds service account credentials using the configuration stored in settings
    and masquerading as the provided user.
    """
    if not SignedJwtAssertionCredentials:
        raise EnvironmentError("Service account can not be used because PyCrypto is not available. Please install PyCrypto.")

    config = get_config()

    if not isinstance(scope, (list, tuple)):
        scope = [scope]

    key = generate_storage_key(config['client_email'], scope, user)
    storage = StorageByKeyName(ServiceAccountStorage, key, 'credentials')

    creds = SignedJwtAssertionCredentials(
        service_account_name=config['client_email'],
        private_key=config['private_key'],
        scope=scope,
        prn=user)
    creds.set_store(storage)

    return creds


class ServiceAccountStorage(ndb.Model):
    """
    Tracks access tokens in the database. The key is
    based on the scopes, user, and clientid
    """
    credentials = CredentialsNDBProperty()

    @classmethod
    def _get_kind(cls):
        return '_argeweb_OAuth2ServiceAccountStorage'


def generate_storage_key(client_id, scopes, user):
    s = u"%s%s%s" % (client_id, sorted(scopes), user)
    hash = hashlib.sha1(s.encode())
    return hash.hexdigest()
