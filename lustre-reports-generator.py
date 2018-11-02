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
import re

import dataset.dataset_handler as ds
import filter.group_filter_handler as gf

from chart.quota_usage_chart import QuotaUsageChart
from chart.disk_quota_usage_chart import DiskQuotaUsageChart
from chart import disk_usage_chart


def raise_option_not_found( section, option ):
   raise Exception( "Option: " + option + " was not found in section: " + section )


def validate_date(date):

   if date:
      
      reg_exp_match = re.match(r'^\d{4}-\d{2}-\d{2}$', date)
      
      if not reg_exp_match:
         raise RuntimeError("No valid date format for date: %s" % date)


def purge_old_report_files(config):

    reports_dir = config.get('base_chart', 'reports_dir')
    pattern = "." + config.get('base_chart', 'file_type')

    if not os.path.isdir(reports_dir):
        raise RuntimeError("Directory does not exist under: %s" % reports_dir)

    file_list = os.listdir(reports_dir)

    for filename in file_list:

        if pattern in filename:

            file_path = os.path.join(reports_dir, filename)

            logging.debug("Removed old report file: %s" % file_path)

            os.remove(file_path)


def create_quota_usage_chart(config, group_info_list):

    # TODO: Remove redundancies with a Superclass!
    logging.debug('Creating bar chart for quota used percentage per group...')

    chart_report_dir = config.get('base_chart', 'reports_dir')
    chart_filename = config.get('bar_chart_quota_used', 'filename')

    now = datetime.datetime.now()
    snapshot_date = now.strftime('%Y-%m-%d')
    snapshot_timestamp = snapshot_date + " - " + now.strftime('%X')

    chart = QuotaUsageChart()

    chart.draw(group_info_list)

    chart_path = os.path.abspath(chart_report_dir + os.path.sep +
                                 chart_filename + "_" + snapshot_date + "." +
                                 chart.file_type)

    chart.save(chart_path)

    logging.debug("Saved bar chart under: %s" % chart_path)


def create_disk_quota_usage_chart(config, group_info_list):

    logging.debug('Creating multi-x bar for quota and disk usage per group...')

    chart_report_dir = config.get('base_chart', 'reports_dir')
    chart_filetype = config.get('base_chart', 'file_type')

    chart_filename = config.get('stacked_bar_quota_disk_used', 'filename')

    now = datetime.datetime.now()
    snapshot_date = now.strftime('%Y-%m-%d')
    snapshot_timestamp = snapshot_date + " - " + now.strftime('%X')

    sorted_group_info_list = sorted(group_info_list,
                                    key=lambda group_info: group_info.quota,
                                    reverse=True)

    chart = DiskQuotaUsageChart()

    chart.draw(sorted_group_info_list)

    chart_path = os.path.abspath(chart_report_dir + os.path.sep +
                                 chart_filename + "_" + snapshot_date + "." +
                                 chart.file_type)

    chart.save(chart_path)

    logging.debug("Saved stacked bar chart under: %s" % chart_path)


def main():

    parser = argparse.ArgumentParser(description='Creates Lustre reports.')
    parser.add_argument('-f', '--config-file', dest='config_file', type=str, required=True, help='Path of the config file.')
    parser.add_argument('-D', '--enable-debug', dest='enable_debug', required=False, action='store_true', help='Enables logging of debug messages.')

    args = parser.parse_args()

    if not os.path.isfile(args.config_file):
        raise IOError("The config file does not exist or is not a file: " + args.config_file)

    logging_level = logging.INFO

    if args.enable_debug:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s: %(message)s')

    logging.info('START')

    try:

        config = ConfigParser.ConfigParser()
        config.read(args.config_file)

        ds.CONFIG = config

        purge_old_report_files(config)
        
        group_info_list = \
            gf.filter_group_info_items(
                ds.get_group_info_list(
                    gf.filter_system_groups(ds.get_group_names())))

        # multiple_x_bar.create_multiple_x_bar(config, group_info_list)

        create_quota_usage_chart(config, group_info_list)

        # pie_chart.create_pie_chart(config)

        logging.info('END')

        return 0
   
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logging.error("Caught exception (%s): %s - %s (line: %s)"
                      % (exc_type, str(e), filename, exc_tb.tb_lineno))


if __name__ == '__main__':
   main()
