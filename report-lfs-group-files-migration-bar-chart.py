#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2019 Gabriele Iannetti <g.iannetti@gsi.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import ConfigParser
import datetime
import argparse
import logging
import sys
import os

import dataset.item_handler as ih
import filter.group_filter_handler as gf

from dataset.lfs_dataset_handler import lustre_total_size
from dataset.lfs_dataset_handler import create_group_info_list
from chart.group_files_migration_bar_chart import GroupFilesMigrationBarChart

from utils.matplotlib_ import check_matplotlib_version
from utils.rsync_ import transfer_report
from utils.getent_group import get_user_groups

from decimal import Decimal


# TODO: Remove config parameter...
def create_report(local_mode, chart_dir, fs1_name, fs2_name, config):

    reports_path_list = list()
    group_info_list = list()
    storage_total_size = 0

    if local_mode:
        group_info_list = ih.create_dummy_group_files_migration_info_list()

    else:

        group_names = get_user_groups()

        files_threshold = int(config.get(
            'group_files_migration_bar_chart', 'files_threshold'))

        fs1 = config.get('storage', 'file_system_1')
        fs2 = config.get('storage', 'file_system_2')

        g1_info_list = create_group_info_list(group_names, fs1)
        g2_info_list = create_group_info_list(group_names, fs2)

        group1_info_items = gf.filter_group_info_items(g1_info_list)
        group2_info_items = gf.filter_group_info_items(g2_info_list)
        
        for gid in group_names:
            
            fs1_files = Decimal(0)
            fs2_files = Decimal(0)
            
            for group1_info_item in group1_info_items:
                
                if gid in group1_info_item.name:

                    fs1_files = group1_info_item.files
                    break

            for group2_info_item in group2_info_items:
                
                if gid in group2_info_item.name:

                    fs2_files = group2_info_item.files
                    break
            
            if fs1_files > files_threshold or fs2_files > files_threshold:

                logging.debug("Append GroupFilesMigrationInfoItem(%s, %s, %s)" % 
                    (gid, fs1_files, fs2_files))
    
                group_info_list.append(ih.GroupFilesMigrationInfoItem(
                    gid, fs1_files, fs2_files))

    # GROUP-FILES-MIGRATION-BAR-CHART
    title = "Group Files Migration Lustre Nyx and Hebe"
    
    chart_path = chart_dir + os.path.sep + config.get( \
        'group_files_migration_bar_chart', 'filename')

    chart = GroupFilesMigrationBarChart(title, group_info_list, chart_path, 
                                        fs1_name, fs2_name)

    chart.create()

    logging.debug("Created chart: %s" % chart_path)
    reports_path_list.append(chart_path)

    return reports_path_list


def main():

    parser = argparse.ArgumentParser(description='Storage Report Generator.')
    parser.add_argument('-f', '--config-file', dest='config_file', type=str, required=True, help='Path of the config file.')
    parser.add_argument('-D', '--enable-debug', dest='enable_debug', required=False, action='store_true', help='Enables logging of debug messages.')
    parser.add_argument('-L', '--enable-local_mode', dest='enable_local', required=False, action='store_true', help='Enables local_mode program execution.')

    args = parser.parse_args()

    if not os.path.isfile(args.config_file):
        raise IOError("The config file does not exist or is not a file: " + args.config_file)

    logging_level = logging.ERROR

    if args.enable_debug:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s: %(message)s')

    try:

        logging.info('START')

        date_now = datetime.datetime.now()

        check_matplotlib_version()

        local_mode = args.enable_local

        logging.debug("Local mode enabled: %s" % local_mode)

        config = ConfigParser.ConfigParser()
        config.read(args.config_file)

        transfer_mode = config.get('execution', 'transfer')

        chart_dir = config.get('base_chart', 'report_dir')

        fs1_name = config.get('storage', 'file_system_name_1')
        fs2_name = config.get('storage', 'file_system_name_2')
        
        chart_path_list = create_report(local_mode, chart_dir, 
                                        fs1_name, fs2_name, config)

        if transfer_mode == 'on':

            for chart_path in chart_path_list:
                transfer_report('weekly', date_now, chart_path, config)

        logging.info('END')

        return 0
   
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        error_msg = "Caught exception (%s): %s - %s (line: %s)" % (
        exc_type, str(e), filename, exc_tb.tb_lineno)

        logging.error(error_msg)


if __name__ == '__main__':
   main()
