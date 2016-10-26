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
        # 從 實體檔案 讀取樣版 (template, themes 相關目錄)
        self.meta.view.template_name = u"/index.html"
        self.context["server_name"] = self.server_name
        self.context["namespace"] = self.namespace
        self.context["information"] = self.host_information
        # 從 Datastore 讀取樣版
        #self.meta.view.template_name = u"assets:/index.html?r=" + str(random.random())

    @route_with(template='/docs/<:(.*)>.html')
    def doc_path(self, path):
        self.meta.view.theme = "prettydocs"
        self.meta.view.template_name = u"/" + path + u".html"
        self.context["docs_name"] = "ArGeWeb"

    @route_with(template='/<:(.*)>.html')
    def all_path(self, path):
        # 從 實體檔案 讀取樣版 (template, themes 相關目錄)
        self.meta.view.template_name = u"/" + path + u".html"

        # 從 Datastore 讀取樣版
        #self.meta.view.template_name = u"assets:/" + path + u".html?r=" + str(random.random())

