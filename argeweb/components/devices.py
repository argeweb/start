

class Devices(object):
    """ Hooks into list to provide automatic detection of (apple) devices """

    def __init__(self, controller):
        self.controller = controller
        self.detect()

    def detect(self):
        uas = self.controller.request.environ.get('HTTP_USER_AGENT', '')

        ua_dict = {
            'user_agent': uas,
            'mobile': (
                "Mobile" in uas or
                "Android" in uas or
                "iP" in uas),
            'ios': ("Mobile" in uas and "AppleWebKit" in uas and "iP" in uas)
        }

        self.controller.context['devices'] = ua_dict
        return ua_dict
