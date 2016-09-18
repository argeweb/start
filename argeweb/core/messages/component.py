from argeweb.core.ndb import ndb
from argeweb.core.response_handlers import ResponseHandler
from argeweb.core.protopigeon import Message, model_message, to_message, messages
import logging

from apiclient.discovery import build

def list_message(message_type):
    name = message_type.__name__ + 'List'
    fields = {
        'items': messages.MessageField(message_type, 1, repeated=True),
        'next_page': messages.StringField(2),
        'previous_page': messages.StringField(3),
        'limit': messages.IntegerField(4),
        'count': messages.IntegerField(5),
        'page': messages.IntegerField(6)
    }
    return type(name, (messages.Message,), fields)


class ErrorMessage(Message):
    errors = messages.StringField(1, repeated=True)


# Install a new int response handler that can detect if
# Errors are present and if so can show them instead of a generic
# 400 error

class IntResponseHandler(ResponseHandler):
    type = int

    def process(self, handler, result):
        handler._clear_redirect()
        if result == 400 and 'messaging' in handler.components and 'errors' in handler.context and handler.components.messaging.transform:
            handler.response = handler.meta.view.render()
            handler.response.status = result
        else:
            handler.abort(result)


class Messaging(object):
    def __init__(self, controller):
        from argeweb.core.scaffold import Scaffolding

        self.controller = controller
        self.transform = False

        # Make sure scaffold is ahead of us
        if Scaffolding in controller.Meta.components:
            if controller.Meta.components.index(Messaging) < controller.Meta.components.index(Scaffolding):
                raise ValueError("Scaffolding must come before Messaging in the component list for controller %s" % controller.name)

        # Create a Message class if needed
        if not hasattr(self.controller.meta, 'Message'):
            if not hasattr(self.controller.meta, 'Model'):
                raise ValueError('Controller.Meta must have a Message or Model class.')
            setattr(self.controller.meta, 'Message', model_message(self.controller.meta.Model))

        # Prefixes to automatically treat as messenging views
        if not hasattr(self.controller.meta, 'messaging_prefixes'):
            setattr(self.controller.meta, 'messaging_prefixes', ('api',))

        # Variable names to check for data
        if not hasattr(self.controller.meta, 'messaging_variable_names'):
            setattr(self.controller.meta, 'messaging_variable_names', ('data',))

        if hasattr(self.controller, 'scaffold'):
            self.controller.meta.messaging_variable_names += (self.controller.scaffold.plural, self.controller.scaffold.singular)

        # Events
        self.controller.events.before_startup += self._on_before_startup
        self.controller.events.before_render += self._on_before_render

    def _on_before_startup(self, controller, *args, **kwargs):
        if controller.route.prefix in self.controller.meta.messaging_prefixes:
            self.activate()

    def activate(self):
        self.transform = True
        self.controller.meta.Parser = 'Message'
        self.controller.meta.change_view('Message')

        if hasattr(self.controller, 'scaffold'):
            self.controller.scaffold.flash_messages = False
            self.controller.scaffold.redirect = False

    __call__ = activate

    def _get_data(self):
        for v in self.controller.meta.messaging_variable_names:
            data = self.controller.context.get(v, None)
            if data:
                return data

    def _transform_data(self, data):
        if isinstance(data, Message):
            return data
        if isinstance(data, (list, ndb.Query)):
            return self._transform_query(data)
        if isinstance(data, ndb.Model):
            return self._transform_entity(data)
        return data

    def _transform_query(self, query):
        ListMessage = list_message(self.controller.meta.Message)
        items = [self._transform_entity(x) for x in query]
        next_page_link = None
        prev_page_link = None
        limit = None
        count = len(items)
        page = None

        if 'pagination' in self.controller.components:
            previous_cursor, current_cursor, next_cursor, page, limit, count = self.controller.components.pagination.get_pagination_info()

            if next_cursor:
                next_page_link = self.controller.uri(_pass_all=True, cursor=next_cursor, _full=True)

            if previous_cursor is not None or page > 1:
                prev_page_link = self.controller.uri(_pass_all=True, cursor=previous_cursor, _full=True)

        return ListMessage(
            items=items,
            next_page=next_page_link,
            previous_page=prev_page_link,
            limit=limit,
            count=count,
            page=page)

    def _transform_entity(self, entity):
        if hasattr(self.controller.meta, 'messaging_transform_function'):
            return self.controller.meta.messaging_transform_function(entity, self.controller.meta.Message)
        return to_message(entity, self.controller.meta.Message)

    def _transform_errors(self):
        errors = self.controller.context.get('errors')
        msg = ErrorMessage(errors=errors)
        return msg

    def render(self):
        if 'errors' in self.controller.context:
            data = self._transform_errors()
        else:
            data = self._get_data()
            data = self._transform_data(data)
        self.controller.context['data'] = data

    def _on_before_render(self, *args, **kwargs):
        if self.transform:
            self.render()
