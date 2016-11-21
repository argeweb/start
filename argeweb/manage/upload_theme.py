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


def run(str_command):
    print str_command
    os.system(str_command)


def main():
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", "--name",
                      action="store", dest="theme_name",
                      help="theme_name that you want to upload [default]")
    parser.add_option("-s", "--server",
                      action="store", dest="server",
                      help="server that you want to upload to")
    parser.add_option("-a", "--account",
                      action="store", dest="account",
                      help="your account on server")
    parser.add_option("-p", "--password",
                      action="store", dest="password",
                      help="your password on server")
    parser.add_option("--save", action="store_true", dest="save", default=False,
                      help="save info into .json")
    parser.add_option("--update", action="store_true", dest="update", default=True,
                      help="update theme information on server")
    parser.add_option("--http", action="store_false", dest="http", default=False,
                      help="using http protocol")
    parser.add_option("--h127", "--s127", action="store_true", dest="h127", default=False,
                      help="using http://127.0.0.1:8080")

    (options, args) = parser.parse_args()

    s = requests.Session()
    paths = (__file__).split(os.path.sep)
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    if paths[-2] == "manage" and paths[-3] == "argeweb":
        manager_dir = script_path
        if options.theme_name is None:
            if len(args) == 0:
                options.theme_name = raw_input("Please enter theme name: ")
            elif len(args) == 1:
                options.theme_name = args[0]
            else:
                print u"error args"
                return
        themes_dir = os.path.join(manager_dir, "..", "..", 'themes', options.theme_name)
    else:
        options.theme_name = paths[-2]
        manager_dir = script_path
        themes_dir = script_path
    file_theme_information = os.path.join(themes_dir, "theme.json")
    if manager_dir == themes_dir:
        file_theme_config = os.path.join(manager_dir, "theme.json")
    else:
        file_theme_config = os.path.join(manager_dir, "theme_%s.json" % options.theme_name)
    temp_config = None
    try:
        with open(file_theme_config, "r+") as f:
            theme_config = json.load(fp=f)
            tmp_host = ("host" in theme_config) and theme_config["host"] or options.server
            tmp_acc = ("account" in theme_config) and theme_config["account"] or options.account
            theme_config.update({
                "host": (tmp_host is not None) and tmp_host or raw_input("server host:  "),
                "account": (tmp_acc is not None) and tmp_acc or raw_input("account:  "),
            })
    except IOError:
        theme_config = {
            "host": (options.server is not None) and options.server or raw_input("server host:  "),
            "account": (options.account is not None) and options.account or raw_input("account:  "),
        }
    if theme_config["host"].endswith("/"):
        theme_config["host"] = theme_config["host"][:-1]
    theme_config["host"] = str(theme_config["host"]).replace("http://", "").replace("https://", "")
    theme_config["host"] = "%s://%s" % ((options.http and "http" or "https"), theme_config["host"])
    if options.h127:
        theme_config["host"] = "http://127.0.0.1:8080"
        print theme_config["host"]
    if options.save:
        j = json.dumps(theme_config, indent=4)
        with open(file_theme_config, "w") as f:
            f.write(j)
            print "config file is save"
    password = ("password" in theme_config) and theme_config["password"] or options.password
    password = (password is not None) and password or getpass.getpass("password: ")
    try:
        print "check :  account"
        r = s.post("%s/admin/login.json" % (theme_config["host"]), data={
            "account": theme_config["account"],
            "password": password
        })
        rn = json.loads(r.text)
        if rn["is_login"] == "false":
            print "return:  account error"
            return
    except:
        print "return:  server error"
        return
    theme_information = {
        "theme_title": "",
        "theme_name": options.theme_name,
        "exclusive": "all",
        "author": "",
        "using": ""
    }
    try:
        with open(file_theme_information, "r+") as f:
            theme_information.update(json.load(fp=f))
            theme_information["theme_title"] = theme_information["name"]
    except IOError:
        pass
    if options.update:
        r = s.post("%s/admin/themes/upload" % (theme_config["host"]), data=theme_information)
    theme_path = "\\themes\\" + options.theme_name
    for root_path, _, files in os.walk(themes_dir):
        for file_name in files:
            if file_name.endswith(".html") or file_name.endswith(".js") or file_name.endswith(".css"):
                path_prue = "/".join((root_path.replace(themes_dir, "") + "\\" + file_name).split("\\"))
                path = "/".join((theme_path + root_path.replace(themes_dir, "") + "\\" + file_name).split("\\"))
                with open(os.path.join(root_path, file_name), 'r') as content_file:
                    content = content_file.read()
                    try:
                        m2 = hashlib.md5()
                        m2.update(content)
                        check_md5 = m2.hexdigest()
                    except:
                        check_md5 = str(time())

                    print "check :  " + path_prue + " --check_md5=" + check_md5
                    r = s.post("%s/admin/code/check" % (theme_config["host"]), data={
                        "check_md5": check_md5,
                        "path": path
                    })
                    rn = json.loads(r.text)
                    if rn["send"] == "true":
                        r = s.post("%s/admin/code/upload" % (theme_config["host"]), data={
                            "code": content,
                            "check_md5": check_md5,
                            "path": path
                        })
                        rn = json.loads(r.text)
                        print "upload:  " + rn["info"]

if __name__ == "__main__":
    main()
