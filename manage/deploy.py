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
os_input = raw_input
if input:
    os_input = input


def raw_input_with_time(str_command):
    return os_input('%s %s' % (datetime.datetime.now().strftime('%H:%M %p'), str_command))


def print_with_time(str_command):
    print ('%s %s' % (datetime.datetime.now().strftime('%H:%M %p'), str_command))


def get_config_file_from(file_path):
    """載入 json 格式的設定檔
    :param file_path: config file path
    :return: config dict
    """
    try:
        with open(file_path, 'r+') as f:
            config = json.load(fp=f)
            return config, False
    except IOError:
        pass
    return None, True


class Deploy:
    config_name = ''
    config = {}

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

        self.dir_manage = path_join(os.path.dirname(os.path.abspath(__file__)))
        self.dir_root = path_join(self.dir_manage, '..')
        self.dir_application = path_join(self.dir_root, 'application')
        self.dir_plugins = path_join(self.dir_root, 'plugins')

        config_name = (len(args) >= 1) and args[0] or raw_input_with_time('Please enter Config Name: ')
        if len(config_name.strip()) == 0:
            config_name = 'default'
        # 先找 manage 目錄下的設定
        config_file_in_manage = path_join(self.dir_manage, 'project_%s.json' % config_name)
        config, no_config_file = get_config_file_from(config_file_in_manage)
        # 再找 applications 下的設定
        if no_config_file:
            config_file_in_application = path_join(path_join(self.dir_application, config_name), 'deploy.json')
            config, no_config_file = get_config_file_from(config_file_in_application)
        self.config, self.config_name = config, config_name

        # 確認要上傳的 project_id 及 版本 ( 命令列 > 設定檔 > 輸入 )
        for key_name in ['project_id', 'version']:
            key_value = getattr(options, key_name)
            if key_value is None and key_name in config:
                key_value = config[key_name]
            config.update({
                key_name: (key_value is not None) and key_value or raw_input_with_time('Please enter %s: ' % key_name)
            })
        if config['version'] == 'auto_today':
            # 自動依今天日期產生版本號、不儲存
            config['version'] = datetime.datetime.today().strftime('%Y%m%d')
        else:
            # 確認是否要儲存設定檔 (若設定檔不存在)
            self.check_and_save_config(no_config_file, options, config_file_in_manage, config)

        self.full_apps, self.target_apps = self.get_applications(config, self.config_name, self.dir_application)
        self.full_plugins, self.target_plugins = self.get_plugins(config, self.dir_plugins)

        # start deploy
        project_id = config['project_id']
        project_version = config['version']
        ignore = self.process_ignore_list()
        include = self.process_include_list()
        update_indexes = options.indexes
        update_cron = options.cron
        rollback = options.rollback
        automatic_scaling = self.process_automatic_scaling_list(config)
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
            elif line.find('includes:') > 0:
                temp_file.write(include)
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

    @staticmethod
    def run(str_command):
        print_with_time(str_command)
        os.system(str_command)

    def merge_yaml(self, file_name, first_line):
        file_need_to_join = []
        for t in self.target_apps:
            yaml_file = path_join(path_join(self.dir_application, t), file_name)
            if os.path.isfile(yaml_file):
                file_need_to_join.append(yaml_file)
        for t in self.target_plugins:
            yaml_file = path_join(path_join(self.dir_plugins, t), file_name)
            if os.path.isfile(yaml_file):
                file_need_to_join.append(yaml_file)

        target_file_name = path_join(self.dir_root, file_name)
        target_file = open(target_file_name, 'w')
        target_file.write(first_line + ':\n')
        for fr in file_need_to_join:
            target_file.write('# %s .\n' % os.path.abspath(fr))
            for line in open(fr, 'r'):
                target_file.write(line)
            target_file.write('\n')
        target_file.close()

    def process_automatic_scaling_list(self, config):
        config_automatic_scaling = []
        if 'automatic_scaling' in config:
            config_automatic_scaling = config['automatic_scaling']
            if isinstance(config_automatic_scaling, basestring):
                config_automatic_scaling = [config_automatic_scaling]
        if isinstance(config_automatic_scaling, list):
            return 'automatic_scaling:\n  '+ '\n  '.join(config_automatic_scaling)
        return ''

    def process_ignore_list(self):
        config_ignore = []
        config = self.config
        full_plugins = self.full_plugins
        target_plugins = self.target_plugins
                
        if 'ignore' in config:
            config_ignore = config['ignore']
            if isinstance(config_ignore, basestring):
                config_ignore = [config_ignore]
        for p in self.full_apps:
            if p not in self.target_apps:
                config_ignore.append("- ^application/%s/.*$" % p)
        for p in self.full_plugins:
            if p not in self.target_plugins:
                config_ignore.append("- ^plugins/%s/.*$" % p)
        if isinstance(config_ignore, list):
            config_ignore = list(set(config_ignore))
            config_ignore.sort()
            return '\n'.join(config_ignore)
        return ''

    def process_include_list(self):
        include_list_in_application = ['includes:']
        for t in self.target_apps:
            yaml_file = path_join(path_join(self.dir_application, t), 'include.yaml')
            if os.path.isfile(yaml_file):
                include_list_in_application.append("- application/%s/include.yaml" % t)
        for t in self.target_plugins:
            yaml_file = path_join(path_join(self.dir_plugins, t), 'include.yaml')
            if os.path.isfile(yaml_file):
                include_list_in_application.append("- plugins/%s/include.yaml" % t)
        return '\n'.join(include_list_in_application)

    def ignore_application_dir(self):
        ignore_list_in_application = []
        for d in os.listdir(self.dir_application):
            if os.path.isdir(path_join(self.dir_application, d)) and d not in self.target_apps:
                ignore_list_in_application.append("- ^application/%s/.*$" % d)
        return ignore_list_in_application

    @staticmethod
    def get_applications(config, config_file, dir_application):
        """取得 application/[project_id] 及設定檔裡的 applications"""
        full_apps = []
        for x in os.listdir(dir_application):
            if os.path.isdir(os.path.join(dir_application, x)):
                full_apps.append(x)
        target_applications = [config['project_id'].replace('-', '_'), config_file]
        if 'applications' in config and isinstance(config['applications'], list):
            target_applications += config['applications']
        return full_apps, list(set(target_applications))

    @staticmethod
    def get_plugins(config, dir_plugins):
        """取得 plugins/[*] 的套件 或 設定檔裡的 plugins"""
        full_plugins = []
        for x in os.listdir(dir_plugins):
            if os.path.isdir(os.path.join(dir_plugins, x)):
                full_plugins.append(x)
        if 'plugins' in config and isinstance(config['plugins'], list):
            target_plugins = config['plugins']
        else:
            target_plugins = full_plugins
        return full_plugins, target_plugins

    def get_application_dir(self):
        application_list = []
        for d in os.listdir(self.dir_application):
            if os.path.isdir(path_join(self.dir_application, d)) and d in self.target_apps:
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

    @staticmethod
    def check_and_save_config(no_config_file, options, config_file_in_manage, config):
        """確認是否要儲存設定檔 (若設定檔不存在)"""
        if no_config_file and options.save is False:
            y = raw_input_with_time('Would you want to save config file (y/N): ')
            options.save = (y == 'y' or y == 'Y')
        if options.save:
            j = json.dumps(config, indent=4)
            with open(config_file_in_manage, 'w') as f:
                f.write(j)
                print_with_time('config file is save')




if __name__ == '__main__':
    Deploy()





















