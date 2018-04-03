import sys
import os
import logging

# Setup the import path
package_dir = 'libs'
package_dir_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), package_dir))

# Allow unzipped libs to be imported
# from libs folder
if not package_dir_path in sys.path:
    sys.path.insert(0, package_dir_path)

# Append zip archives to path for zipimport
if os.path.exists(package_dir_path):
    file_list = []
    for filename in os.listdir(package_dir_path):
        if filename.endswith(('.zip', '.egg')):
            path = os.path.join(package_dir_path, filename)
            try:
                if not path in sys.path:
                    file_list.append(filename)
                    sys.path.insert(0, path)
            except:
                logging.error('Can not Add zip package %s ' % filename)
    if len(file_list) > 0:
        logging.debug('Adding zip the follower package to path\n    %s' % '\n    '.join(file_list))
