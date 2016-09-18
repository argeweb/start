

class Behavior(object):
    """
    Behavior mimics all of the callbacks in the Model class to allow you to stack unrelated
    callbacks together
    """
    def __init__(self, Model):
        self.Model = Model

    def before_put(self, instance):
        pass

    def after_put(self, instance):
        pass

    def before_delete(self, key):
        pass

    def after_delete(self, key):
        pass

    def before_get(self, key):
        pass

    def after_get(self, item):
        pass
