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
    @staticmethod
    def run(str_command):
        print str_command
        os.system(str_command)

    def deploy(self, project_id, project_version='2016', ignore='', update_indexes=True, update_cron=False, rollback=False):
        if project_id is None or project_id == '':
            print 'need project id'
            return
        os.chdir(self.base_dir)
        temp_deploy_yaml_file = os.path.join(self.base_dir, 'temp_deploy.yaml')
        app_yaml_file = os.path.join(self.base_dir, 'app.yaml')
        temp_file = open(temp_deploy_yaml_file, 'w+')
        app_file = open(app_yaml_file)
        # temp_file.write("version: %s\n" % project_version)
        for line in app_file:
            if line.find('ssl') > 0:
                temp_file.write('- name: ssl\n  version: latest\n')
            else:
                temp_file.write(line)
        temp_file.write(ignore)
        app_file.close()
        temp_file.close()
        if rollback:
            self.run('appcfg.py rollback temp_deploy.yaml -A %s -V %s' % (project_id, project_version))
        else:
            self.run('appcfg.py update temp_deploy.yaml -A %s -V %s' % (project_id, project_version))
        if update_indexes:
            self.process_index_yaml(project_id, project_version)
        if update_cron:
            self.run('appcfg.py update_cron  . -A %s -V %s' % (project_id, project_version))
        os.remove(temp_deploy_yaml_file)

    def process_index_yaml(self, project_id, project_version):
        file_need_to_join = self.get_index_yaml_file(self.plugins_dir)
        for p in self.get_application_dir():
            file_need_to_join += self.get_index_yaml_file(p)
        index_yaml_file = os.path.join(self.base_dir, 'index.yaml')
        target_file = open(index_yaml_file, 'w')
        target_file.write('indexes:\n')
        for fr in file_need_to_join:
            target_file.write('# %s .\n' % os.path.abspath(fr))
            for line in open(fr, 'r'):
                target_file.write(line)
            target_file.write('\n')
        target_file.close()
        self.get_index_yaml_file(self.application_dir)
        self.run('appcfg.py update_indexes . -A %s -V %s' % (project_id, project_version))

    def process_ignore_list(self, project_config):
        project_config_ignore = []
        if 'ignore' in project_config:
            project_config_ignore = project_config['ignore']
            if isinstance(project_config_ignore, basestring):
                project_config_ignore = [project_config_ignore]
        project_config_ignore += self.ignore_application_dir()
        ignore = ''
        if isinstance(project_config_ignore, list):
            ignore = '\n'.join(project_config_ignore)
        return ignore

    def ignore_application_dir(self):
        dir_app = os.path.join(self.base_dir, 'application')
        ignore_list_in_application = []
        for d in os.listdir(dir_app):
            if os.path.isdir(os.path.join(dir_app, d)) and d not in self.target_applications:
                ignore_list_in_application.append("- ^application/%s/.*$" % d)
        return ignore_list_in_application

    @staticmethod
    def get_target_applications(project_config, project_config_file):
        target_applications = [project_config['project_id'], project_config_file]
        if 'applications' in project_config and isinstance(project_config['applications'], list):
            target_applications += project_config['applications']
        return target_applications

    def get_application_dir(self):
        application_list = []
        for d in os.listdir(self.application_dir):
            if os.path.isdir(os.path.join(self.application_dir, d)) and d in self.target_applications:
                application_list.append(os.path.join(self.application_dir, d))
        return application_list

    @staticmethod
    def get_index_yaml_file(path):
        index_yaml_files = []
        for root_path, _, files in os.walk(path):
            if root_path[len(path) + 1:].count(os.sep) < 2:
                for file_name in files:
                    if file_name == 'index.yaml':
                        index_yaml_files.append(os.path.join(root_path, file_name))
        return index_yaml_files

    def __init__(self):
        parser = OptionParser(usage='usage: %prog theme_name [options]')
        parser.add_option('-A', '--project_id',
                          action='store', dest='project_id',
                          default=None,
                          help='project_id that you want to upload')
        parser.add_option('-V', '--version',
                          default=None,
                          action='store', dest='version',
                          help='version that you want to upload')
        parser.add_option('-I', '--indexes', action='store_true', dest='indexes', default=False,
                          help='also update indexes (default: True)')
        parser.add_option('-C', '--cron', action='store_true', dest='cron', default=False,
                          help='also update cron')
        parser.add_option('-R', '--rollback', action='store_true', dest='rollback', default=False,
                          help='rollback')
        parser.add_option('--save', action='store_true', dest='save', default=False,
                          help='save info into .json')

        (options, args) = parser.parse_args()
        
        project_config_file = 'default'
        if len(sys.argv) >= 2:
            project_config_file = sys.argv[1]
        dir_web = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        file_project_config = os.path.join(dir_web, 'project_%s.json' % project_config_file)
        project_config = {}
        try:
            with open(file_project_config, "r+") as f:
                project_config = json.load(fp=f)
        except IOError:
            pass
        if options.project_id is None:
            project_id = ('project_id' in project_config) and project_config['project_id'] or options.project_id
        else:
            project_id = options.project_id
        if options.version is None:
            version = ('version' in project_config) and project_config['version'] or options.version
        else:
            version = options.version
        project_config.update({
            'project_id': (project_id is not None) and project_id or raw_input('Please enter Project id: '),
            'version': (version is not None) and version or raw_input('Please enter version:  '),
        })
        if options.save:
            j = json.dumps(project_config, indent=4)
            with open(file_project_config, 'w') as f:
                f.write(j)
                print 'config file is save'
        if project_config['version'] == 'auto_today':
            import datetime
            project_config['version'] = datetime.datetime.today().strftime('%Y%m%d')
        self.base_dir = os.path.join(dir_web, '..')
        self.application_dir = os.path.join(self.base_dir, 'application')
        self.plugins_dir = os.path.join(self.base_dir, 'plugins')
        self.target_applications = self.get_target_applications(project_config, project_config_file)
        project_config['ignore'] = self.process_ignore_list(project_config)
        self.deploy(project_config['project_id'], project_config['version'], project_config['ignore'], options.indexes, options.cron, options.rollback)

if __name__ == '__main__':
    Deploy()