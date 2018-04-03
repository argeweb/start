#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import getpass
import hashlib
from optparse import OptionParser
from time import time
import OpenSSL
import six
import _cffi_backend

import os.path


def get_md5(content):
    try:
        m2 = hashlib.md5()
        m2.update(content)
        return m2.hexdigest()
    except:
        return str(time())


def check_file_with_server_files(path, path_prue, files_on_server, check_md5):
    for item in files_on_server:
        if u'/' + item['path'] == u'%s' % path and item['md5'] == u'%s' % check_md5:
            return False
    print ' upload  : ' + check_md5 + '  ' + path_prue
    return True


def run(str_command):
    print str_command
    os.system(str_command)

print '============================================================'
print ' ArgeWeb theme upload Tool'
print ' This tool can help you to upload theme to the sever'
print ' You need to give tool the sever url, account and password'
print '============================================================'

try:
    file_path = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    file_path = os.path.dirname(os.path.abspath(sys.argv[0]))

requests_session = requests.Session()
cacert_path = os.path.join(file_path, 'cacert.pem')
if os.path.exists(cacert_path):
    print ' cacert  : ' + cacert_path
    os.environ['REQUESTS_CA_BUNDLE'] = cacert_path
    requests.utils.DEFAULT_CA_BUNDLE_PATH = cacert_path
    requests_session.verify = cacert_path


theme_config = None
usage = "usage: %prog theme_name [options]"
parser = OptionParser(usage=usage)
parser.add_option('-n', '--name',
                  action='store', dest='theme_name',
                  help='theme_name that you want to upload')
parser.add_option('-s', '--server',
                  action='store', dest='server',
                  help='server that you want to upload to')
parser.add_option('-a', '--account',
                  action='store', dest='account',
                  help='your account on server')
parser.add_option('-p', '--password',
                  action='store', dest='password',
                  help='your password on server')
parser.add_option('--save', action='store_true', dest='save', default=False,
                  help='save info into .json')
parser.add_option('--update', action='store_true', dest='update', default=True,
                  help='update theme information on server')
parser.add_option('--http', action='store_false', dest='http', default=False,
                  help='using http protocol')
parser.add_option('-d', '--dev', action='store_true', dest='dev', default=False,
                  help='using http://127.0.0.1:8080')

(options, args) = parser.parse_args()
paths = file_path.split(os.path.sep)
if len(paths) == 1:
    if os.path.sep == '\\':
        paths = file_path.split('/')
    else:
        paths = file_path.split('\\')
script_path = file_path
if 'manage' in paths and 'argeweb' in paths:
    manager_dir = script_path
    if options.theme_name is None:
        if len(args) == 0:
            options.theme_name = raw_input(' Please enter theme name: ')
        elif len(args) == 1:
            options.theme_name = args[0]
        else:
            print u'error args'
            sys.exit()
        if options.theme_name is '' or options.theme_name is u'':
            print u'error need theme name'
            sys.exit()
    themes_dir = os.path.join(manager_dir, '..', '..', 'themes', options.theme_name)
else:
    options.theme_name = paths[-1]
    manager_dir = script_path
    themes_dir = script_path
if manager_dir == themes_dir:
    file_theme_config = os.path.join(manager_dir, 'theme.json')
else:
    file_theme_config = os.path.join(manager_dir, 'theme_%s.json' % options.theme_name)
temp_config = None
try:
    with open(file_theme_config, 'r+') as f:
        theme_config = json.load(fp=f)
        tmp_host = options.server is not None and options.server or theme_config['host']
        tmp_acc = options.account is not None and options.account or theme_config['account']
        theme_config.update({
            'host': (tmp_host is not None) and tmp_host or raw_input(' server  : '),
            'account': (tmp_acc is not None) and tmp_acc or raw_input(' account : '),
        })
except:
    theme_config = {
        'host': (options.server is not None) and options.server or raw_input(' server  : '),
        'account': (options.account is not None) and options.account or raw_input(' account : '),
    }
if theme_config['host'].endswith('/'):
    theme_config['host'] = theme_config['host'][:-1]
if options.dev:
    theme_config['host'] = 'http://127.0.0.1:8080'
if str(theme_config['host']).find('http://') >= 0:
    options.http = True
    requests_session.verify = False
theme_config['host'] = str(theme_config['host']).replace('http://', '').replace('https://', '')
theme_config['host'] = '%s://%s' % ((options.http and 'http' or 'https'), theme_config['host'])
if options.save:
    j = json.dumps(theme_config, indent=4)
    try:
        with open(file_theme_config, 'w') as f:
            f.write(j)
            print ' config  : file is save'
    except:
        pass

password = ('password' in theme_config) and theme_config['password'] or options.password
password = (password is not None) and password or getpass.getpass(' password: ')

print ' server  : ' + theme_config['host']
r = requests_session.post('%s/admin/login.json' % (theme_config['host']), data={
    'account': theme_config['account'],
    'password': password
})
rn = json.loads(r.text)
if rn['is_login'] == 'false':
    print r.text
    print ' login   : account error'
    sys.exit()
else:
    print ' login   : success'

theme_information = {
    'theme_title': options.theme_name,
    'theme_name': options.theme_name,
    'exclusive': 'all',
    'author': '',
    'using': '',
    'thumbnail': ''
}
try:
    theme_information.update(theme_config)
except IOError:
    pass
if options.update:
    r = requests_session.post('%s/admin/themes/themes/upload' % (theme_config['host']), data=theme_information)
    print ' update  : theme information is update'
r = requests_session.post('%s/admin/themes/themes/delete_theme' % (theme_config['host']), data={'theme': theme_information['theme_name']})
print r
print ' done'
