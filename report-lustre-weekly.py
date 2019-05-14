#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2018 Gabriele Iannetti <g.iannetti@gsi.de>
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

import dataset.lfs_dataset_handler as ldh
import dataset.item_handler as ih

import filter.group_filter_handler as gf

from chart.quota_pct_bar_chart import QuotaPctBarChart
from chart.usage_quota_bar_chart import UsageQuotaBarChart
from chart.usage_pie_chart import UsagePieChart

from utils.matplotlib_ import check_matplotlib_version
from utils.rsync_ import transfer_report
from utils.getent_group import get_all_group_names


def create_weekly_reports(local_mode,
                          chart_dir,
                          file_system,
                          fs_long_name,
                          quota_pct_bar_chart,
                          usage_quota_bar_chart,
                          usage_pie_chart,
                          num_top_groups):

    reports_path_list = list()

    group_info_list = None
    storage_total_size = 0

    if local_mode:

        group_info_list = ih.create_dummy_group_info_list()
        storage_total_size = 18458963071860736

    else:
        
        group_names_list = gf.filter_system_groups(get_all_group_names())

        group_info_list = \
            gf.filter_group_info_items(
                ldh.create_group_info_list(group_names_list, file_system))

        storage_total_size = ldh.lustre_total_size(file_system)
    
    # QUOTA-PCT-BAR-CHART
    title = "Group Quota Usage on %s" % fs_long_name
    chart_path = chart_dir + os.path.sep + quota_pct_bar_chart
    chart = QuotaPctBarChart(title, group_info_list, chart_path)
    chart.create()

    logging.debug("Created chart: %s" % chart_path)
    reports_path_list.append(chart_path)

    # USAGE-QUOTA-BAR-CHART
    title = "Quota and Disk Space Usage on %s" % fs_long_name
    chart_path = chart_dir + os.path.sep + usage_quota_bar_chart
    chart = UsageQuotaBarChart(title, group_info_list, chart_path)
    chart.create()

    logging.debug("Created chart: %s" % chart_path)
    reports_path_list.append(chart_path)

    # USAGE-PIE-CHART
    title = "Storage Usage on %s" % fs_long_name
    chart_path = chart_dir + os.path.sep + usage_pie_chart
    chart = UsagePieChart(title,
                          group_info_list,
                          chart_path,
                          storage_total_size,
                          num_top_groups)
    chart.create()

    logging.debug("Created chart: %s" % chart_path)
    reports_path_list.append(chart_path)

    return reports_path_list


def main():

    parser = argparse.ArgumentParser(description='Storage Report Generator.')
    
    parser.add_argument('-f', '--config-file', dest='config_file', 
        type=str, required=True, help='Path of the config file.')
    
    parser.add_argument('-D', '--enable-debug', dest='enable_debug', 
        required=False, action='store_true', 
        help='Enables logging of debug messages.')
    
    parser.add_argument('-L', '--enable-local_mode', dest='enable_local', 
        required=False, action='store_true', 
        help='Enables local_mode program execution.')

    args = parser.parse_args()

    if not os.path.isfile(args.config_file):
        raise IOError("The config file does not exist or is not a file: %s" % 
            args.config_file)

    logging_level = logging.INFO

    if args.enable_debug:
        logging_level = logging.DEBUG

    logging.basicConfig(
        level=logging_level, format='%(asctime)s - %(levelname)s: %(message)s')

    try:

        logging.debug('START')

        date_now = datetime.datetime.now()

        check_matplotlib_version()

        local_mode = args.enable_local

        logging.debug("Local mode enabled: %s" % local_mode)

        config = ConfigParser.ConfigParser()
        config.read(args.config_file)

        transfer_mode = config.get('execution', 'transfer')

        chart_dir = config.get('base_chart', 'report_dir')

        file_system = config.get('storage', 'file_system')
        fs_long_name = config.get('storage', 'fs_long_name')
        
        quota_pct_bar_chart = config.get('quota_pct_bar_chart', 'filename')
        usage_quota_bar_chart = config.get('usage_quota_bar_chart', 'filename')
        usage_pie_chart = config.get('usage_pie_chart', 'filename')
        
        num_top_groups = config.getint('usage_pie_chart', 'num_top_groups')

        chart_path_list = \
            create_weekly_reports(local_mode,
                                  chart_dir,
                                  file_system,
                                  fs_long_name,
                                  quota_pct_bar_chart,
                                  usage_quota_bar_chart,
                                  usage_pie_chart,
                                  num_top_groups)

        if transfer_mode == 'on':

            for chart_path in chart_path_list:
                transfer_report('weekly', date_now, chart_path, config)

        logging.debug('END')

        return 0
   
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        error_msg = "Caught exception (%s): %s - %s (line: %s)" % (
        exc_type, str(e), filename, exc_tb.tb_lineno)

        logging.error(error_msg)


if __name__ == '__main__':
   main()
