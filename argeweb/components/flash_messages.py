class FlashMessages(object):
    """
    Flash Messages are brief messages that are stored in the session and displayed to the user on
    the next page. These are useful for things like create/edit/delete acknowledgements.
    """

    def __init__(self, controller):
        self.controller = controller
        self.controller.events.before_render += self._on_before_render

    def flash(self, message, level='info'):
        """
        Adds the given message to the dictionary of "flash" messages to show to the user on the next page.
        """
        flash = self.controller.session.get('__flash', {})

        if level == 'error':
            level = 'danger'
        import time
        if isinstance(flash, list):
            flash = {}
        flash[time.time()] = {"message": message, "level": level}
        self.controller.session['__flash'] = flash

    def messages(self, clear=True):
        """
        returns all flash messsages, and by default clears the queue
        """
        flashes = self.controller.session.get('__flash', None) or {}

        if clear:
            self.controller.session['__flash'] = {}
        return flashes

    def _on_before_render(self, controller, *args, **kwargs):
        controller.context.set_dotted('this.flash_messages', self.messages().items)

    __call__ = flash
