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

import dataset.lustre_dataset_handler as ds
import filter.group_filter_handler as gf
from lfs.disk_usage_info import lustre_total_size

from chart.quota_pct_bar_chart import QuotaPctBarChart
from chart.usage_quota_bar_chart import UsageQuotaBarChart
from chart.usage_pie_chart import UsagePieChart


def validate_date(date):

   if date:
      
      reg_exp_match = re.match(r'^\d{4}-\d{2}-\d{2}$', date)
      
      if not reg_exp_match:
         raise RuntimeError("No valid date format for date: %s" % date)


def purge_old_report_files(report_dir):

    pattern = ".svg"

    if not os.path.isdir(report_dir):
        raise RuntimeError("Directory does not exist under: %s" % report_dir)

    file_list = os.listdir(report_dir)

    for filename in file_list:

        if pattern in filename:

            file_path = os.path.join(report_dir, filename)

            logging.debug("Removed old report file: %s" % file_path)

            os.remove(file_path)


def create_prev_year_kw():

    now = datetime.datetime.now()
    first = now.replace(day=1)
    prev_month = first - datetime.timedelta(days=1)
    return prev_month.strftime('%Y-%V')


def create_chart_path(chart_dir, chart_filename,
                      short_name, prev_year_kw):

    chart_filename = chart_filename.replace('{SHORTNAME}', short_name)
    chart_filename = chart_filename.replace('{TIMEPOINT}', prev_year_kw)

    return chart_dir + os.path.sep + chart_filename


def create_usage_pie_chart(title, file_path,
                           group_info_list, storage_total_size):

    chart = UsagePieChart(title=title,
                          file_path=file_path,
                          dataset=group_info_list,
                          storage_total_size=storage_total_size)

    chart.create()


def create_quota_pct_bar_chart(title, file_path, group_info_list):

    chart = QuotaPctBarChart(title=title,
                             sub_title='Procedural Usage per Group',
                             file_path=file_path,
                             dataset=group_info_list)

    chart.create()


def create_usage_quota_bar_chart(title, file_path, group_info_list):

    chart = UsageQuotaBarChart(
        title=title,
        file_path=file_path,
        dataset=group_info_list)

    chart.create()


def main():

    parser = argparse.ArgumentParser(description='Storage Report Generator.')
    parser.add_argument('-f', '--config-file', dest='config_file', type=str, required=True, help='Path of the config file.')
    parser.add_argument('-D', '--enable-debug', dest='enable_debug', required=False, action='store_true', help='Enables logging of debug messages.')
    parser.add_argument('-L', '--enable-local', dest='enable_local', required=False, action='store_true', help='Enables local program execution.')

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

        group_info_list = None
        storage_total_size = 0

        if args.enable_local:

            logging.debug('Run Mode: LOCAL/DEV')

            group_info_list = ds.create_dummy_group_info_list()
            storage_total_size = 18458963071860736

        else:

            logging.debug('Run Mode: PRODUCTIVE')

            ds.CONFIG = config

            group_info_list = \
                gf.filter_group_info_items(
                    ds.get_group_info_list(
                        gf.filter_system_groups(ds.get_group_names())))

            storage_total_size = \
                lustre_total_size(config.get('storage', 'filesystem'))

        prev_year_kw = create_prev_year_kw()
        chart_dir = config.get('base_chart', 'report_dir')
        long_name = config.get('storage', 'long_name')
        short_name = config.get('storage', 'short_name')

        purge_old_report_files(chart_dir)

        # QUOTA-PCT-BAR-CHART
        title = "Group Quota Usage on %s" % long_name

        chart_path = create_chart_path(
            chart_dir,
            config.get('quota_pct_bar_chart', 'filename'),
            short_name,
            prev_year_kw)

        create_quota_pct_bar_chart(title, chart_path, group_info_list)


        # USAGE-QUOTA-BAR-CHART
        title = "Quota and Disk Space Usage on %s" % long_name

        chart_path = create_chart_path(
            chart_dir,
            config.get('usage_quota_bar_chart', 'filename'),
            short_name,
            prev_year_kw)

        create_usage_quota_bar_chart(title, chart_path, group_info_list)

        # USAGE-PIE-CHART
        title = "Storage Usage on %s" % long_name

        chart_path = create_chart_path(
            chart_dir,
            config.get('usage_pie_chart', 'filename'),
            short_name,
            prev_year_kw)

        create_usage_pie_chart(title, chart_path,
                               group_info_list, storage_total_size)

        logging.info('END')

        return 0
   
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logging.error("Caught exception (%s): %s - %s (line: %s)"
                      % (exc_type, str(e), filename, exc_tb.tb_lineno))


if __name__ == '__main__':
   main()
