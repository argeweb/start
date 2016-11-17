#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/11/9


#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import sys


def run(str_command):
    print str_command
    os.system(str_command)

project_config_file = "project"
if len(sys.argv) == 2:
    project_config_file = sys.argv[1]
dir_web = os.path.join(os.path.dirname(os.path.abspath(__file__)))
file_project_config = os.path.join(dir_web, "%s.json" % project_config_file)

try:
    with open(file_project_config , "r+") as f:
        project_config = json.load(fp=f)
except IOError:
    project_config = {
        "id": raw_input("Please enter Project name: "),
        "version": raw_input("Please enter version: ")
    }
    j = json.dumps(project_config, indent=4)
    with open(file_project_config, "w") as f:
        f.write(j)


def deploy(project_id="argeweb-framework", project_version= "2016"):
    dir_web = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",  "..")
    os.chdir(dir_web)
    temp_file = open(os.path.join(dir_web, "temp_deploy.yaml"), 'w+')
    app_file = open(os.path.join(dir_web, "app.yaml"))
    # temp_file.write("version: %s\n" % project_version)
    for line in app_file:
        if line.find("ssl") > 0:
            temp_file.write("- name: ssl\n  version: latest\n")
        else:
            temp_file.write(line)
    if "ignore" in project_config and project_config["ignore"].find("themes") >= 0:
        temp_file.write("\n- ^themes/.*$")
    app_file.close()
    temp_file.close()
    # run ("gcloud app deploy app.yaml --project argeweb-framework")
    run("appcfg.py update temp_deploy.yaml -A %s -V %s" %(project_id, project_version))
    run("appcfg.py update_indexes . -A %s -V %s" %(project_id, project_version))

    os.remove(os.path.join(dir_web, "temp_deploy.yaml"))

os.chdir(dir_web)
deploy(project_config["id"], project_config["version"])
