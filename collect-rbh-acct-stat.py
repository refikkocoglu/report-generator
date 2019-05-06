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
import smtplib
import time
import sys
import os

from contextlib import closing
from email.mime.text import MIMEText


def create_acct_history_table(cur, db, table):
   
    sql = "USE " + db

    logging.debug(sql)
    cur.execute(sql)
   
    sql = """
CREATE TABLE """ + table + """ (
   uid varbinary(127) NOT NULL DEFAULT 'unknown',
   gid varbinary(127) NOT NULL DEFAULT 'unknown',
   size bigint(20) unsigned DEFAULT '0',
   count bigint(20) unsigned DEFAULT '0',
   date date NOT NULL,
   PRIMARY KEY (uid,gid,date)
) ENGINE=MyISAM DEFAULT CHARSET=latin1
"""
   
    cur.execute(sql)
    logging.debug("Created table:\n%s" % sql)


def take_acct_stat_snapshot(cur, rbh_db, rbh_acct_table, history_db, history_acct_table, date):
       
    sql = "INSERT INTO %s.%s SELECT uid, gid, SUM(size), SUM(count), '%s' FROM %s.%s GROUP BY 1,2" \
          % (history_db, history_acct_table, date, rbh_db, rbh_acct_table)
   
    logging.debug(sql)
    cur.execute(sql)
   
    if not cur.rowcount:
        raise RuntimeError("Snapshot failed for date: %s." % date)
   
    logging.debug("Inserted rows: %d into table: %s for date: %s" % 
        (cur.rowcount, history_acct_table, date))


def main():

    try:

        parser = argparse.ArgumentParser(description='Fills Robinhood acct history table.')

        parser.add_argument('-f', '--config-file', dest='config_file', type=str,
                            required=True, help='Path of the config file.')

        parser.add_argument('-D', '--enable-debug', dest='enable_debug',
                            required=False, action='store_true', help='Enables logging of debug messages.')

        parser.add_argument('--create-table', dest='create_table',
                            required=False, action='store_true', help='If set the accounting history table is created.')

        args = parser.parse_args()

        if not os.path.isfile(args.config_file):
            raise IOError("The config file does not exist or is not a file: %s" % args.config_file)

        logging_level = logging.INFO

        if args.enable_debug:
            logging_level = logging.DEBUG

        logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s: %(message)s')

        logging.debug('START')

        config = ConfigParser.ConfigParser()
        config.read(args.config_file)

        date_today = time.strftime('%Y-%m-%d')

        rbh_db = config.get('robinhood', 'database')
        rbh_acct_table = config.get('robinhood', 'table')

        history_db = config.get('history', 'database')
        history_acct_table = config.get('history', 'table')

        with closing(MySQLdb.connect(host=config.get('mysqld', 'host'),
                                   user=config.get('mysqld', 'user'),
                                   passwd=config.get('mysqld', 'password'),
                                   db=rbh_db)) as conn:

            with closing(conn.cursor()) as cur:

                conn.autocommit(True)

                if args.create_table:
                    create_acct_history_table(cur, history_db, history_acct_table)

                take_acct_stat_snapshot(cur, rbh_db, rbh_acct_table, history_db, history_acct_table, date_today)

        logging.debug('END')

        exit(0)
   
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        error_msg = "Caught exception (%s): %s - %s (line: %s)" % 
            (exc_type, str(e), filename, exc_tb.tb_lineno)

        logging.error(error_msg)

        try:

            mail_server = config.get('mail', 'server')
            mail_sender = config.get('mail', 'sender')
            mail_recipient = config.get('mail', 'recipient')

            msg = MIMEText(error_msg)
            msg['Subject'] = __file__ + " - Error Occured!"
            msg['From'] = mail_sender
            msg['To'] = mail_recipient

            smtp_conn = smtplib.SMTP(mail_server)
            smtp_conn.sendmail(mail_sender, mail_recipient.split(','), msg.as_string())
            smtp_conn.quit()

        except Exception as e:

            logging.error("Mail send failed: %s" % e)

            exit(2)

        exit(1)


if __name__ == '__main__':
    main()
