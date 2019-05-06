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

import dataset.lustre_dataset_handler as ldh
import dataset.item_handler as ih

import filter.group_filter_handler as gf

from chart.trend_chart import TrendChart

from utils.matplotlib_ import check_matplotlib_version
from utils.rsync_ import transfer_report
from utils.pandas_ import create_data_frame

import dateutil.relativedelta


def create_usage_trend_chart(local_mode, long_name, chart_dir, start_date, end_date, config):

    if local_mode:
        item_list = ih.create_dummy_group_date_values(8, 1000)

    else:

        ldh.CONFIG = config

        groups = gf.filter_system_groups(ldh.get_group_names())

        threshold = config.get('usage_trend_chart', 'threshold')

        filtered_group_names = ldh.filter_groups_at_threshold_size(start_date, end_date, threshold, groups)

        item_list = ldh.get_time_series_group_sizes(start_date, end_date, filtered_group_names)

    group_item_dict = ih.create_group_date_value_item_dict(item_list)

    data_frame = create_data_frame(group_item_dict)

    title = "Top Groups Usage Trend on %s" % long_name

    chart_path = chart_dir + os.path.sep + config.get('usage_trend_chart', 'filename')

    chart = TrendChart(title, data_frame, chart_path, 'Time (Weeks)', 'Disk Space Used (TiB)')

    chart.create()

    return chart_path


def create_quota_trend_chart(local_mode, long_name, chart_dir, start_date, end_date, config):

    if local_mode:
        item_list = ih.create_dummy_group_date_values(50, 200)

    else:

        ldh.CONFIG = config

        groups = gf.filter_system_groups(ldh.get_group_names())

        item_list = ldh.get_time_series_group_quota_usage(start_date, end_date, groups)

    group_item_dict = ih.create_group_date_value_item_dict(item_list)

    data_frame = create_data_frame(group_item_dict)

    title = "Group Quota Trend on %s" % long_name

    chart_path = chart_dir + os.path.sep + config.get('quota_trend_chart', 'filename')

    chart = TrendChart(title, data_frame, chart_path, 'Time (Weeks)', 'Quota Used (%)')

    chart.create()

    return chart_path


def main():

    parser = argparse.ArgumentParser(description='Lustre Monthly Report Generator')

    parser.add_argument('-f', '--config-file', dest='config_file', type=str,
                        required=True, help='Path of the config file.')

    parser.add_argument('-D', '--enable-debug', dest='enable_debug',
                        required=False, action='store_true',
                        help='Enables logging of debug messages.')

    parser.add_argument('-L', '--enable-local_mode', dest='enable_local',
                        required=False, action='store_true',
                        help='Enables local_mode program execution.')

    args = parser.parse_args()

    if not os.path.isfile(args.config_file):
        raise IOError("The config file does not exist or is not a file: %s" % args.config_file)

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

        date_format = config.get("time_series_chart", "date_format")
        prev_months = config.getint("time_series_chart", "prev_months")

        if prev_months <= 0:
            raise RuntimeError("Config parameter 'prev_months' must be greater than 0!")

        prev_date = date_now - dateutil.relativedelta.relativedelta(months=prev_months)

        start_date = prev_date.strftime(date_format)
        end_date = date_now.strftime(date_format)

        logging.debug("Time series start date: %s" % start_date)

        chart_path_list = list()

        chart_path = create_usage_trend_chart(local_mode, long_name, chart_dir, start_date, end_date, config)
        logging.debug("Created chart: %s" % chart_path)
        chart_path_list.append(chart_path)

        chart_path = create_quota_trend_chart(local_mode, long_name, chart_dir, start_date, end_date, config)
        logging.debug("Created chart: %s" % chart_path)
        chart_path_list.append(chart_path)

        if transfer_mode == 'on':

            for chart_path in chart_path_list:
                transfer_report('monthly', date_now, chart_path, config)

        raise RuntimeError('TEST')

        logging.debug('END')

        return 0

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        error_msg = "Caught exception (%s): %s - %s (line: %s)" % (exc_type, str(e), filename, exc_tb.tb_lineno)

        logging.error(error_msg)


if __name__ == '__main__':
    main()
