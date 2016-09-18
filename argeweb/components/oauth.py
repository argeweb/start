from google.appengine.api import users
from argeweb.core.decorator import decorator
from argeweb.core.oauth2.session import Session as OAuth2Session
from argeweb.core.oauth2.user_credentials import UserCredentials as OAuth2UserCredentials
from oauth2client.client import AccessTokenRefreshError
import httplib2
import webapp2


class OAuth(object):
    """
    The OAuth component handles providing credentials to your handler's actions and automatically initiating the flow to acquire credentials if needed.
    """

    name = 'oauth'

    def _set_scopes(self, scopes):
        if not isinstance(scopes, list):
            scopes = [scopes]
        self._scopes = scopes

    def _get_scopes(self):
        return self._scopes

    scopes = property(_get_scopes, _set_scopes)

    force_prompt = False

    def __init__(self, controller):
        if hasattr(controller.meta, 'oauth_scopes'):
            self._scopes = controller.meta.oauth_scopes
        else:
            self._scopes = []
        self._user_credentials = None
        setattr(controller, 'oauth', self)
        self.controller = controller

    def credentials(self):
        """
        Returns an Oauth2Credentials object that can be used to sign a request
        """
        if self._user_credentials:
            return self._user_credentials.credentials

    def user_credentials(self):
        return self._user_credentials

    def has_credentials(self):
        """
        Returns true if credentials exist for the current user.
        """
        return self._user_credentials and self._user_credentials.credentials and not self._user_credentials.credentials.invalid

    def http(self):
        """
        Returns a signed httplib2.Http instance that can be readily used for making authorized requests.
        """
        if self.has_credentials():
            return self._user_credentials.credentials.authorize(httplib2.Http())

    def authorization_url(self, redirect=None, admin=False, force_prompt=False):
        """
        Generates an authorization url to start the OAuth flow for the current user.
        """
        return self._create_oauth_session(self.controller, admin, redirect, force_prompt)

    def _create_oauth_session(self, controller, admin=False, redirect=None, force_prompt=False):
        if admin and not users.is_current_user_admin():
            webapp2.abort(500, 'The server does not have the needed authorization to complete the request')

        if not redirect:
            redirect = controller.request.url

        session = OAuth2Session(scopes=self._scopes, redirect=redirect, admin=admin, force_prompt=force_prompt)
        session.put()
        uri = controller.uri('oauth:start', session=session.key.urlsafe())
        return uri


@decorator
def require_credentials(method, controller, *args, **kwargs):
    """
    Requires that valid credentials exist for the current user before executing the controller.
    Will redirect the user for authorization.
    User controller.oauth_scopes to specify which scopes are required.
    """
    oauth = controller.components.oauth
    user_credentials = OAuth2UserCredentials.find(user=controller.user, scopes=oauth.scopes, admin=False)
    oauth._user_credentials = user_credentials
    if not oauth.has_credentials():
        return controller.redirect(oauth.authorization_url(admin=False, force_prompt=oauth.force_prompt))

    try:
        return method(controller, *args, **kwargs)
    except AccessTokenRefreshError:
        return controller.redirect(oauth.authorization_url(admin=False, force_prompt=oauth.force_prompt))


@decorator
def provide_credentials(method, controller, *args, **kwargs):
    """
    Similar to :func:`require_credentials` but instead of automatically redirecting the user when credentials are required it allows you to take your own action.

    You can use :meth:`OAuth.has_credentials()` to interrogate.
    """
    oauth = controller.components.oauth
    user_credentials = OAuth2UserCredentials.find(user=controller.user, scopes=oauth.scopes, admin=False)
    oauth._user_credentials = user_credentials
    return method(controller, *args, **kwargs)


@decorator
def require_admin_credentials(method, controller, *args, **kwargs):
    """
    Requires that valid credentials exist for the administrator before executing the controller.
    Will redirect the user for authorization if the user is an admin.
    """
    oauth = controller.components.oauth
    user_credentials = OAuth2UserCredentials.find(scopes=oauth.scopes, admin=True)
    oauth._user_credentials = user_credentials
    if not oauth.has_credentials():
        return controller.redirect(oauth.authorization_url(admin=True))

    try:
        return method(controller, *args, **kwargs)
    except AccessTokenRefreshError:
        return controller.redirect(oauth.authorization_url(admin=True))
