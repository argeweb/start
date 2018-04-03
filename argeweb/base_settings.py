#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/22.

settings = dict()
# 應用程式設定
settings['application'] = {}
settings['application']['name'] = u'ArGeWeb'
settings['application']['custom_error'] = True
settings['application']['message_timeout'] = 28800

# 驗証失敗時，重新導向路徑
settings['authorization_redirect'] = []
settings['authorization_redirect'].append({'authorization': 'require_member', 'redirect': '/'})
settings['authorization_redirect'].append({'authorization': 'require_admin', 'redirect': '/admin/login'})
settings['authorization_redirect'].append({'authorization': 'require_user', 'redirect': '/login.html'})

# 時區
settings['timezone'] = {}
settings['timezone']['local'] = 'Asia/Taipei'
# 設定用來寄送郵件的相關設定
settings['email'] = {}
settings['email']['sender'] = None

# app stats
settings['appstats'] = {
    'enabled': True,
    'enabled_live': False
}

# app stats
settings['debug'] = {
    'enabled': True,
    'enabled_live': False
}

settings['app_config'] = {
    'webapp2_extras.sessions': {
        # WebApp2 encrypted cookie key
        # You can use a UUID generator like http://www.famkruithof.net/uuid/uuidgen
        'secret_key': 'abfe8060-d76a-4169-bd51-09f592d4a8db',
    },
    'webapp2_extras.jinja2': {
        'template_path': 'templates',
        'environment_args': {'extensions': ['jinja2.ext.i18n']}
    }
}

# 上傳檔案存放區
settings['upload'] = {
    # Whether to use Cloud Storage (default) or the blobstore to store uploaded files.
    'use_cloud_storage': False,
    # The Cloud Storage bucket to use. Leave as "None" to use the default GCS bucket.
    # See here for info: https://developers.google.com/appengine/docs/python/googlecloudstorageclient/activate#Using_the_Default_GCS_Bucket
    'bucket': 'abc'
}