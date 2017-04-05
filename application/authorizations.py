#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/1/28.
from argeweb import auth


def require_member(controller):
    """
    Requires that a user is logged in
    """
    application_user = None
    mobile = None
    if 'application_user_key' in controller.session and controller.session['application_user_key'] is not None:
        # 使用帳密進行登入者
        application_user = controller.session['application_user_key'].get()

    if application_user is None:
        return False, 'require_member'
    if application_user is None:
        return False, 'require_member'
    role = application_user.check_and_get_role('user') or application_user.check_and_get_role('member')
    if role is None:
        return False, 'require_member'
    controller.mobile = mobile
    controller.application_user = application_user
    controller.context['application_user_key'] = application_user.key
    controller.session['application_user_key'] = application_user.key
    action_name = '.'.join(str(controller).split(' object')[0][1:].split('.')[0:-1]) + '.' + controller.route.action

    if controller.application_user.has_permission(action_name) is False:
        return controller.abort(403)
    return True

require_member_for_prefix = auth.predicate_chain(auth.prefix_predicate, require_member)
require_member_for_action = auth.predicate_chain(auth.action_predicate, require_member)
require_member_for_route = auth.predicate_chain(auth.route_predicate, require_member)

application_authorizations = (auth.require_admin_for_prefix(prefix=('admin',)),)