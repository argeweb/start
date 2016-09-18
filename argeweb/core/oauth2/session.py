"""
OAuth dance session
"""

from google.appengine.ext import ndb
from argeweb.core.ndb import Model
from oauth2client.appengine import FlowNDBProperty


class Session(Model):

    scopes = ndb.StringProperty(indexed=False, repeated=True)
    admin = ndb.BooleanProperty(indexed=False)
    force_prompt = ndb.BooleanProperty(indexed=False)
    redirect = ndb.StringProperty(indexed=False)
    flow = FlowNDBProperty(indexed=False)

    @classmethod
    def _get_kind(cls):
        return '_argeweb_oauth2_session'
