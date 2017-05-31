#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/3/3
from argeweb import auth, add_authorizations
from argeweb import Controller, route_with, scaffold, BasicModel, route_menu, route
from argeweb import Pagination
from argeweb.components.search import Search
import random


class Home(Controller):
    class Meta:
        title = u'前台'
        components = (scaffold.Scaffolding, Pagination, Search)

