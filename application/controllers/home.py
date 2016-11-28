#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/3/3
from argeweb import add_authorizations
from argeweb import Controller, route_with, scaffold, BasicModel, route_menu, route
from argeweb import Pagination
from argeweb.components.search import Search
import random


class Home(Controller):
    class Meta:
        title = u"前台"
        components = (scaffold.Scaffolding, Pagination, Search)

    @route_with('/')
    @route_with('/index.html')
    def index(self):
        # 取消樣版系統的快取
        self.meta.view.cache = False

        # 先從 Datastore 讀取樣版, 再從 實體檔案 讀取樣版 (template, themes 相關目錄)
        self.meta.view.template_name = [u"assets:/themes/%s/index.html" % self.theme, u"/index.html"]
        if self.theme == "default":
            # 若有語系參數的話 ( hl )
            index_path = u"%s.html" % self.params.get_string("hl", u"index").lower().replace("-", "")
            self.meta.view.template_name = [u"assets:/themes/%s/%s" % (self.theme, index_path), index_path]
        self.context["information"] = self.host_information

    @route_with(template='/<:(.*)>.html')
    def all_path(self, path):
        # 取消樣版系統的快取
        self.meta.view.cache = False

        self.context["information"] = self.host_information
        # 先從 Datastore 讀取樣版, 再從 實體檔案 讀取樣版 (template, themes 相關目錄)
        self.meta.view.template_name = [
            u"assets:/themes/%s/%s.html" % (self.theme, path), u"/" + path + u".html"]

    @route_with(template='/docs/<:(.*)>.html')
    def doc_path(self, path):
        # ArgeWeb 說明文件使用
        self.meta.view.theme = "prettydocs"
        self.meta.view.template_name = u"/" + path + u".html"
        self.context["docs_name"] = "ArGeWeb"

