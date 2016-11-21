#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2016/11/9
from optparse import OptionParser
import os
import json
import sys


class Deploy:
    @classmethod
    def run(cls, str_command):
        print str_command
        os.system(str_command)

    def deploy(self, project_id="argeweb-framework", project_version="2016", ignore=""):
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
        temp_file.write(ignore)
        app_file.close()
        temp_file.close()
        # run ("gcloud app deploy app.yaml --project argeweb-framework")
        self.run("appcfg.py update temp_deploy.yaml -A %s -V %s" %(project_id, project_version))
        self.run("appcfg.py update_indexes . -A %s -V %s" %(project_id, project_version))

        os.remove(os.path.join(dir_web, "temp_deploy.yaml"))

    def __init__(self):
        usage = "usage: %prog theme_name [options]"
        parser = OptionParser(usage=usage)
        parser.add_option("-A", "--project_id",
                          action="store", dest="project_id",
                          default=None,
                          help="project_id that you want to upload")
        parser.add_option("-V", "--version",
                          default=None,
                          action="store", dest="version",
                          help="version that you want to upload")
        parser.add_option("--save", action="store_true", dest="save", default=False,
                          help="save info into .json")

        (options, args) = parser.parse_args()
        
        project_config_file = "project"
        if len(sys.argv) == 2:
            project_config_file = sys.argv[1]
        dir_web = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        file_project_config = os.path.join(dir_web, "%s.json" % project_config_file)
        project_config = {}
        try:
            with open(file_project_config , "r+") as f:
                project_config = json.load(fp=f)
        except IOError:
            pass
        if options.project_id is None:
            project_id = ("project_id" in project_config) and project_config["project_id"] or options.project_id
        else:
            project_id = options.project_id
        if options.version is None:
            version = ("version" in project_config) and project_config["version"] or options.version
        else:
            version = options.version
        project_config.update({
            "project_id": (project_id is not None) and project_id or raw_input("Please enter Project id: "),
            "version": (version is not None) and version or raw_input("Please enter version:  "),
            "ignore": ""
        })
        if options.save:
            j = json.dumps(project_config, indent=4)
            with open(file_project_config, "w") as f:
                f.write(j)
                print "config file is save"
        if project_config["version"] == "date_today":
            import datetime
            project_config["version"] = datetime.datetime.today().strftime("%Y%m%d")
        if "ignore" in project_config and project_config["ignore"].find("themes") >= 0:
            project_config["ignore"] = "\n- ^themes/.*$"
        os.chdir(dir_web)
        print project_config["version"]
        self.deploy(project_config["project_id"], project_config["version"], project_config["ignore"])

if __name__ == "__main__":
    Deploy()