#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/1/28.
from argeweb import auth


def require_orderplus_user(controller):
    """
    Requires that a user is logged in
    """
    from application.models.mobile_model import get_mobile, get_mobile_with_account
    application_user = None
    mobile = None
    if "mobile" in controller.session and controller.session["mobile"] is not None:
        # 使用手機進行登入者
        number = controller.session["mobile"]
        mobile = get_mobile(number)
        application_user = mobile.account.get()
    if "application_user_key" in controller.session and controller.session["application_user_key"] is not None:
        # 使用帳密進行登入者
        application_user = controller.session["application_user_key"].get()
        mobile = get_mobile_with_account(application_user.key)

    if application_user is None:
        return False, "require_orderplus_user"
    if application_user is None:
        return False, "require_orderplus_user"
    if application_user.role is None:
        return False, "require_orderplus_user"
    role = application_user.role.get()
    if role is None:
        return False, "require_orderplus_user"
    controller.mobile = mobile
    controller.application_user = application_user
    controller.application_user_level = role.level
    controller.prohibited_actions = str(role.prohibited_actions).split(",")
    controller.context["application_user_level"] = controller.application_user_level
    controller.context["application_user_key"] = application_user.key
    controller.session["application_user_key"] = application_user.key
    if controller.route.name in controller.prohibited_actions:
        return controller.abort(403)
    return True

require_orderplus_user_for_prefix = auth.predicate_chain(auth.prefix_predicate, require_orderplus_user)
require_orderplus_user_for_action = auth.predicate_chain(auth.action_predicate, require_orderplus_user)
require_orderplus_user_for_route = auth.predicate_chain(auth.route_predicate, require_orderplus_user)

orderplus_authorizations = (auth.require_admin_for_prefix(prefix=('admin',)),
                          require_orderplus_user_for_prefix(prefix=('dashboard',)))