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

from lfs.disk_usage_info import lustre_total_size
from lfs.retrieve_quota import create_group_info_item

from chart.usage_pie_chart import UsagePieChart

from utils.matplotlib_ import check_matplotlib_version
from utils.rsync_ import transfer_report
from utils.getent_group import get_all_group_names


def create_weekly_reports(local_mode, chart_dir, long_name, config):

    reports_path_list = list()
    group_info_items = None
    storage_total_size = 0

    if local_mode:

        group_info_items = ih.create_dummy_group_info_items()
        storage_total_size = 18458963071860736

    else:

        fs_name = config.get('storage', 'filesystem')
        
        storage_total_size = lustre_total_size(fs_name)
        
        group_names = gf.filter_system_groups(get_all_group_names())

        buffered_group_info_items = list()
        
        # TODO: move filling of group_info_items to ldh,
        #       but split the ldh from rbh stuff 
        #       to be independent of mysql connector
        for grp_name in group_names:
            
            # TODO: add lfs prefix!!!
            buffered_group_info_items.append(
                create_group_info_item(grp_name, fs_name))
            
        group_info_items = \
            gf.filter_group_info_items(buffered_group_info_items)

    # USAGE-PIE-CHART
    title = "Storage Usage on %s" % long_name
    chart_path = chart_dir + os.path.sep + config.get('usage_pie_chart', 'filename')
    num_top_groups = config.getint('usage_pie_chart', 'num_top_groups')
    chart = UsagePieChart(title, group_info_items, chart_path, storage_total_size, num_top_groups)
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

    logging_level = logging.INFO

    if args.enable_debug:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s: %(message)s')

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
        long_name = config.get('storage', 'long_name')

        chart_path_list = create_weekly_reports(local_mode, chart_dir, long_name, config)

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
