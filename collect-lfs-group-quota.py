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

import dataset.rbh_dataset_handler as rdh

from contextlib import closing
from dataset.lfs_dataset_handler import retrieve_group_quota


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
   quota bigint(20) unsigned DEFAULT '0',
   PRIMARY KEY (gid,date)
) ENGINE=MyISAM DEFAULT CHARSET=latin1
"""
            logging.debug(sql)
            cur.execute(sql)


def save_group_quota_map(config, date, iter_items):

    table = config.get('history', 'table')

    with closing(MySQLdb.connect(host=config.get('mysqld', 'host'),
                                 user=config.get('mysqld', 'user'),
                                 passwd=config.get('mysqld', 'password'),
                                 db=config.get('history', 'database'))) as conn:

        with closing(conn.cursor()) as cur:

            sql = "INSERT INTO %s (date, gid, quota) VALUES" % table

            gid, quota = next(iter_items)

            sql += "('%s', '%s', %s)" % (date, gid, quota)

            for gid, quota in iter_items:
                sql += ", ('%s', '%s', %s)" % (date, gid, quota)

            logging.debug(sql)
            cur.execute(sql)

            if not cur.rowcount:
                raise RuntimeError("Snapshot failed for date: %s." % date)

            logging.debug("Inserted rows: %d into table: %s for date: %s"
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

        rdh.CONFIG = config

        if args.create_table:

            create_group_quota_history_table(config)

            logging.debug('END')

            exit(0)

        fs = config.get('lustre', 'file_system')

        group_quota_map = dict()

        group_names = rdh.get_group_names()
        
        for gid in group_names:

            try:
                quota = retrieve_group_quota(gid, fs)

                logging.debug("GID: %s - Quota: %d" % (gid, quota))

                group_quota_map[gid] = quota

            except Exception as e:

                logging.warning("Skipped quota for group: %s" % gid)

                exc_type, exc_obj, exc_tb = sys.exc_info()
                filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                logging.error("Exception (type: %s): %s - %s (line: %s)" %
                              (exc_type, str(e), filename, exc_tb.tb_lineno))

        if run_mode == 'print':

            for key, value in group_quota_map.iteritems():
                print("%s:%s" % (key, value))

        if run_mode == 'collect':

            iter_items = group_quota_map.iteritems()

            save_group_quota_map(config, date_today, iter_items)
        
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
