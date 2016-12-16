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
    if application_user.role is None:
        return False, 'require_member'
    role = application_user.role.get()
    if role is None:
        return False, 'require_member'
    controller.mobile = mobile
    controller.application_user = application_user
    controller.application_user_level = role.level
    controller.prohibited_actions = str(role.prohibited_actions).split(',')
    controller.context['application_user_level'] = controller.application_user_level
    controller.context['application_user_key'] = application_user.key
    controller.session['application_user_key'] = application_user.key
    if controller.route.name in controller.prohibited_actions:
        return controller.abort(403)
    return True

require_member_for_prefix = auth.predicate_chain(auth.prefix_predicate, require_member)
require_member_for_action = auth.predicate_chain(auth.action_predicate, require_member)
require_member_for_route = auth.predicate_chain(auth.route_predicate, require_member)

application_authorizations = (auth.require_admin_for_prefix(prefix=('admin',)),)