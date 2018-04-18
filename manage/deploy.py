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
import datetime

path_join = os.path.join


def raw_input_with_time(str_command):
    return raw_input('%s %s' % (datetime.datetime.now().strftime('%H:%M %p'), str_command))


def print_with_time(str_command):
    print '%s %s' % (datetime.datetime.now().strftime('%H:%M %p'), str_command)


class Deploy:
    @staticmethod
    def run(str_command):
        print_with_time(str_command)
        os.system(str_command)

    def merge_yaml(self, file_name, first_line):
        file_need_to_join = self.get_files(self.dir_plugins, file_name)
        for p in self.get_application_dir():
            file_need_to_join += self.get_files(p, file_name)
        target_file_name = path_join(self.dir_root, file_name)
        target_file = open(target_file_name, 'w')
        target_file.write(first_line + ':\n')
        for fr in file_need_to_join:
            target_file.write('# %s .\n' % os.path.abspath(fr))
            for line in open(fr, 'r'):
                target_file.write(line)
            target_file.write('\n')
        target_file.close()

    def process_automatic_scaling_list(self, project_config):
        project_config_automatic_scaling = []
        if 'automatic_scaling' in project_config:
            project_config_automatic_scaling = project_config['automatic_scaling']
            if isinstance(project_config_automatic_scaling, basestring):
                project_config_automatic_scaling = [project_config_automatic_scaling]
        if isinstance(project_config_automatic_scaling, list):
            return 'automatic_scaling:\n  '+ '\n  '.join(project_config_automatic_scaling)
        return ''

    def process_ignore_list(self, project_config):
        project_config_ignore = []
        if 'ignore' in project_config:
            project_config_ignore = project_config['ignore']
            if isinstance(project_config_ignore, basestring):
                project_config_ignore = [project_config_ignore]
        project_config_ignore += self.ignore_application_dir()
        if isinstance(project_config_ignore, list):
            return '\n'.join(project_config_ignore)
        return ''

    def ignore_application_dir(self):
        ignore_list_in_application = []
        for d in os.listdir(self.dir_application):
            if os.path.isdir(path_join(self.dir_application, d)) and d not in self.target_applications:
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
        for d in os.listdir(self.dir_application):
            if os.path.isdir(path_join(self.dir_application, d)) and d in self.target_applications:
                application_list.append(path_join(self.dir_application, d))
        return application_list

    @staticmethod
    def get_files(path, target_file_name):
        index_yaml_files = []
        for root_path, _, files in os.walk(path):
            if root_path[len(path) + 1:].count(os.sep) < 2:
                for file_name in files:
                    if file_name == target_file_name:
                        index_yaml_files.append(path_join(root_path, file_name))
        return index_yaml_files

    def __init__(self):
        parser = OptionParser(usage='usage: %prog deploy [options]')
        parser.add_option('-A', '--project_id',
                          action='store', dest='project_id',
                          default=None,
                          help='project_id that you want to upload')
        parser.add_option('-V', '--version',
                          default=None,
                          action='store', dest='version',
                          help='version that you want to upload')
        parser.add_option('-I', '--indexes', action='store_true', dest='indexes', default=False,
                          help='also update indexes (default: False)')
        parser.add_option('-C', '--cron', action='store_true', dest='cron', default=False,
                          help='also update cron (default: False)')
        parser.add_option('-R', '--rollback', action='store_true', dest='rollback', default=False,
                          help='rollback application first (default: False)')
        parser.add_option('-S', '--save', action='store_true', dest='save', default=False,
                          help='rollback application first (default: False)')

        (options, args) = parser.parse_args()

        project_config_name = 'default'
        if len(sys.argv) == 1:
            project_config_name = raw_input_with_time('Please enter Project Name: ')
        if len(sys.argv) >= 2:
            project_config_name = sys.argv[1]
        
        self.dir_manage = path_join(os.path.dirname(os.path.abspath(__file__)))
        self.dir_root = path_join(self.dir_manage, '..')
        self.dir_application = path_join(self.dir_root, 'application')
        self.dir_plugins = path_join(self.dir_root, 'plugins')

        project_config = {}
        no_config_file = True
        try:
            config_file_in_manage = path_join(self.dir_manage, 'project_%s.json' % project_config_name)
            with open(config_file_in_manage, 'r+') as f:
                project_config = json.load(fp=f)
                no_config_file = False
        except IOError:
            pass
        try:
            config_file_in_application = path_join(path_join(self.dir_application, project_config_name), 'deploy.json')
            print config_file_in_application
            with open(config_file_in_application, 'r+') as f:
                project_config = json.load(fp=f)
                no_config_file = False
        except IOError:
            pass
        for n in ['project_id', 'version']:
            n_val = getattr(options, n)
            if n_val is None and n in project_config:
                n_val = project_config[n]
            project_config.update({
                n: (n_val is not None) and n_val or raw_input_with_time('Please enter %s: ' % n)
            })
        if project_config['version'] == 'auto_today':
            project_config['version'] = datetime.datetime.today().strftime('%Y%m%d')
        else:
            if no_config_file and options.save is False:
                y = raw_input_with_time('Would you want to save config file (y/N): ')
                options.save = (y == 'y' or y == 'Y')
            if options.save:
                j = json.dumps(project_config, indent=4)
                with open(config_file_in_manage, 'w') as f:
                    f.write(j)
                    print_with_time('config file is save')
        self.target_applications = self.get_target_applications(project_config, project_config_name)

        # start deploy
        project_id = project_config['project_id']
        project_version = project_config['version']
        ignore = self.process_ignore_list(project_config)
        update_indexes = options.indexes
        update_cron = options.cron
        rollback = options.rollback
        automatic_scaling = self.process_automatic_scaling_list(project_config)
        if project_id is None or project_id == '':
            print_with_time('need project id')
            return

        os.chdir(self.dir_root)
        temp_deploy_yaml_file = path_join(self.dir_root, 'temp_deploy.yaml')
        app_yaml_file = path_join(self.dir_root, 'app.yaml')
        temp_file = open(temp_deploy_yaml_file, 'w+')
        app_file = open(app_yaml_file)
        # temp_file.write("version: %s\n" % project_version)
        for line in app_file:
            if line.find('ssl') > 0:
                temp_file.write('- name: ssl\n  version: latest\n')
            elif line.find('automatic_scaling') > 0:
                if automatic_scaling is not None and automatic_scaling != '':
                    temp_file.write(automatic_scaling+'\n')
            else:
                temp_file.write(line)
        temp_file.write(ignore)
        app_file.close()
        temp_file.close()
        if rollback:
            self.run('appcfg.py rollback temp_deploy.yaml -A %s -V %s' % (project_id, project_version))
        self.run('appcfg.py update temp_deploy.yaml -A %s -V %s' % (project_id, project_version))
        if update_indexes:
            self.merge_yaml('index.yaml', 'indexes')
            self.run('appcfg.py update_indexes . -A %s -V %s' % (project_id, project_version))
        if update_cron:
            self.merge_yaml('cron.yaml', 'cron')
            self.run('appcfg.py update_cron . -A %s -V %s' % (project_id, project_version))
        os.remove(temp_deploy_yaml_file)


if __name__ == '__main__':
    Deploy()





















