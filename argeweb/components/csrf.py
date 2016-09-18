import uuid
from argeweb.core.controller import add_authorizations


class CSRF(object):
    """
    Provides protection against `Cross-site Request Forgery <http://en.wikipedia.org/wiki/Cross-site_request_forgery>`_.

    Example::

        class Pages(Controller):
            class Meta:
                components = (Scaffolding, CSRF)

            admin_list = scaffold.list

            @csrf_protect
            def admin_add(self):
                return scaffold.add(self)

    Scaffold will automatically ensure the csrf token is part of the form. For non-scaffold forms you
    will need to add {{csrf}} inside of your form.
    """
    def __init__(self, controller):
        self.controller = controller
        self.controller.events.before_render += self._on_before_render
        self.controller.meta.view.events.before_form_fields += self._on_before_form_fields

    def _on_before_render(self, controller, *args, **kwargs):
        controller.context['csrf'] = create_csrf_field(generate_csrf_token(controller))

    def _on_before_form_fields(self):
        a = self.controller.context.get('csrf')
        return a

def generate_csrf_token(controller):
    """ Generates a new csrf token and stores it in the session"""
    session = controller.session
    if '_csrf_token' not in session:
        session['_csrf_token'] = uuid.uuid4()
    return session['_csrf_token']


def create_csrf_field(token):
    return '<input type="hidden" name="csrf_token" value="%s">' % token


def require_csrf(controller):
    """
    Authorization chain that validates the CSRF token.
    """
    if controller.request.method in ('POST', 'PUT') and not controller.request.path.startswith('/taskqueue'):
        token = controller.session.get('_csrf_token')
        if not token or str(token) != str(controller.request.get('csrf_token')):
            return False, "Cross-site request forgery failure"
    return True


def csrf_protect(f):
    """
    Shortcut decorator to easily add the CSRF check to an action
    """
    return add_authorizations(require_csrf)(f)
