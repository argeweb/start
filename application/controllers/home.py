#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/3/3
from argeweb import ndb
from argeweb import add_authorizations
from argeweb import Controller, route_with, scaffold, BasicModel, route_menu, route
from argeweb import Pagination
from argeweb.components.search import Search
import random


class Home(Controller):
    class Meta:
        title = u"前台"
        components = (scaffold.Scaffolding, Pagination, Search)
        pagination_limit = 10

    @route_with('/')
    @route_with('/index.html')
    def index(self):
        pass

    @route_with(template='/<:(.*)>.html')
    def all_path(self, path):
        self.meta.view.template_name = u"assets:/" + path + u".html?r=" + str(random.random())
        # self.meta.view.template_name = u"code:中文 aaaaa {{ function ('ge_information', hostname=framework.hostname) }}"
        # return {"path": path}

