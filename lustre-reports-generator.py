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
import argparse
import logging
import sys
import os
import re

import dataset.dataset_handler as ds
import filter.group_filter_handler as gf

from chart import pie_chart
from chart import bar_chart
from chart import multiple_x_bar


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

        multiple_x_bar.create_multiple_x_bar(config, group_info_list)

        bar_chart.create_bar_chart(config, group_info_list)

        pie_chart.create_pie_chart(config)

        logging.info('END')

        return 0
   
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        logging.error("Caught exception (%s): %s - %s (line: %s)"
                      % (exc_type, str(e), filename, exc_tb.tb_lineno))


if __name__ == '__main__':
   main()
