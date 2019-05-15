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
import logging
import argparse
import MySQLdb
import time
import sys
import os

import dataset.lfs_dataset_handler as ldh

from contextlib import closing
from utils.getent_group import get_user_groups


def create_group_quota_history_table(config):

    db = config.get('history', 'database')
    table = config.get('history', 'table')

    with closing(MySQLdb.connect(host=config.get('mysqld', 'host'),
                                 user=config.get('mysqld', 'user'),
                                 passwd=config.get('mysqld', 'password'),
                                 db=db)) as conn:

        with closing(conn.cursor()) as cur:

            conn.autocommit(True)

            sql = "USE " + db

            logging.debug(sql)
            cur.execute(sql)

            sql = """
CREATE TABLE """ + table + """ (
   date date NOT NULL,
   gid varbinary(127) NOT NULL DEFAULT 'unknown',
   used bigint(20) unsigned DEFAULT NULL,
   quota bigint(20) unsigned DEFAULT '0',
   files bigint(20) unsigned DEFAULT '0',
   PRIMARY KEY (gid,date)
) ENGINE=MyISAM DEFAULT CHARSET=latin1
"""
            logging.debug(sql)
            cur.execute(sql)


def store_group_quota(config, date, group_info_list):

    table = config.get('history', 'table')

    with closing(MySQLdb.connect(host=config.get('mysqld', 'host'),
                                 user=config.get('mysqld', 'user'),
                                 passwd=config.get('mysqld', 'password'),
                                 db=config.get('history', 'database'))) \
                                    as conn:

        with closing(conn.cursor()) as cur:

            sql = "INSERT INTO %s (date, gid, used, quota, files) VALUES" \
                % table
            
            iter_list = iter(group_info_list)

            item = next(iter_list)

            sql += "('%s', '%s', %s, %s, %s)" \
                % (date, item.name, item.size, item.quota, item.files)

            for item in iter_list:
                sql += ", ('%s', '%s', %s, %s, %s)" \
                    % (date, item.name, item.size, item.quota, item.files)

            logging.debug(sql)
            cur.execute(sql)

            if not cur.rowcount:
                raise RuntimeError("Snapshot failed for date: %s." % date)

            logging.debug("Inserted rows: %d into table: %s for date: %s" \
                % (cur.rowcount, table, date))


def main():

    # Default run-mode: collect
    run_mode = 'collect'

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-f', '--config-file', dest='config_file', type=str,
        required=True, help='Path of the config file.')
    
    parser.add_argument('-m', '--run-mode', dest='run_mode', type=str,
        default=run_mode, required=False,
        help="Specifies the run mode: 'print' or 'collect' - Default: %s" %
            run_mode)

    parser.add_argument('-D', '--enable-debug', dest='enable_debug',
        required=False, action='store_true',
        help='Enables logging of debug messages.')

    parser.add_argument('--create-table', dest='create_table',
        required=False, action='store_true',
        help='Creates the group quota history table.')

    args = parser.parse_args()

    if not os.path.isfile(args.config_file):
        raise IOError("The config file does not exist or is not a file: %s" 
            % args.config_file)
    
    logging_level = logging.INFO

    if args.enable_debug:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level,
                        format='%(asctime)s - %(levelname)s: %(message)s')

    if not (args.run_mode == 'print' or args.run_mode == 'collect'):
        raise RuntimeError("Invalid run mode: %s" % args.run_mode)
    else:
        run_mode = args.run_mode

    try:
        logging.debug('START')

        date_today = time.strftime('%Y-%m-%d')
        
        config = ConfigParser.ConfigParser()
        config.read(args.config_file)

        if args.create_table:

            create_group_quota_history_table(config)

            logging.debug('END')

            exit(0)

        fs = config.get('lustre', 'file_system')

        group_info_list = ldh.create_group_info_list(get_user_groups(), fs)

        if run_mode == 'print':

            for group_info in group_info_list:

                logging.info(
                    "Group: '%s' - Used: '%s' - Quota: '%s' - Files: '%s'" \
                        % (group_info.name,
                           group_info.size, 
                           group_info.quota, 
                           group_info.files))

        if run_mode == 'collect':
            store_group_quota(config, date_today, group_info_list)

        logging.debug('END')

        exit(0)

    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        error_msg = "Caught exception (%s): %s - %s (line: %s)" % \
                    (exc_type, str(e), filename, exc_tb.tb_lineno)

        logging.error(error_msg)

        exit(1)


if __name__ == '__main__':
    main()
