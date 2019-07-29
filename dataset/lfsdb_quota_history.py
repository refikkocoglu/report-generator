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


import MySQLdb
import logging

from contextlib import closing

from dataset.item_handler import GroupDateValueItem


class QuotaHistoryTable:

    def __init__(self, host, user, passwd, db, table):

        self._host = host
        self._user = user
        self._passwd = passwd
        self._db = db
        self._table = table

    def filter_groups_at_threshold(self,
                                   start_date,
                                   end_date,
                                   threshold,
                                   groups=None):
        """
        Returns a list of group names that reached a certain threshold at size.
        :param start_date: Specifies the start date.
        :param end_date: Specifies the end date.
        :param threshold: Specifies the threshold for the size of groups.
        :param groups: Specifies the group names to filter for (optional).
        :return: A list of group names.
        """

        results = list()
    
        with closing(MySQLdb.connect(host=self._host,
                                     user=self._user,
                                     passwd=self._passwd,
                                     db=self._db)) \
                                        as conn:
    
            with closing(conn.cursor()) as cur:
    
                sql = "SELECT gid "\
                      "FROM %s "\
                      "WHERE date BETWEEN '%s' AND '%s' "\
                      % (self._table, start_date, end_date)
    
                if groups:
                    sql += "AND gid IN (%s) " % str(groups).strip('[]')
    
                sql += "AND used >= %s "\
                       "GROUP BY gid"\
                       % threshold
    
                logging.debug(sql)
                cur.execute(sql)
    
                for item in cur.fetchall():
                    results.append(item[0])
    
        return results

    def get_time_series_group_sizes(self, start_date, end_date, groups=None):
        """
        Queries ACCT_STAT_HISTORY table for given group names
        within a specific time interval filled with size consumption per day.
        The size consumption is saved on base of TiB.
        :param start_date: Start date of the time interval.
        :param end_date: End date of the time interval.
        :param groups: List of group names (optional).
        :return: A list of GroupDateValueItem.
        """

        results = list()

        with closing(MySQLdb.connect(host=self._host,
                                     user=self._user,
                                     passwd=self._passwd,
                                     db=self._db)) \
                                        as conn:

            with closing(conn.cursor()) as cur:

                # TiB Divisor = '1099511627776'
                sql = "SELECT gid, "\
                      "       date, "\
                      "       ROUND(used/1099511627776) as used "\
                      "FROM %s WHERE date between '%s' AND '%s' "\
                      % (self._table, start_date, end_date)

                if groups:
                    sql += "AND gid IN (%s) " % str(groups).strip('[]')
    
                sql += 'GROUP BY gid, date'

                logging.debug(sql)
                cur.execute(sql)

                for item in cur.fetchall():

                    name = item[0]
                    date = item[1]
                    used = None

                    if item[2]:
                        used = int(item[2])

                    results.append(GroupDateValueItem(name, date, used))

                if not results:
                    raise RuntimeError("Found empty result list!")

        return results

    def get_time_series_group_quota_usage(self, 
                                          start_date, 
                                          end_date, 
                                          groups=None):
        """
        Queries GROUP-QUOTA-History table for given groups
        within a specific time interval for quota consumption in percentage.
        :param start_date: Start date of the time interval.
        :param end_date: End date of the time interval.
        :param groups: List of group names (optional).
        :return: A list of GroupDateValueItem.
        """

        results = list()

        with closing(MySQLdb.connect(host=self._host,
                                     user=self._user,
                                     passwd=self._passwd,
                                     db=self._db)) \
                                        as conn:
    
            with closing(conn.cursor()) as cur:
    
                sql = "SELECT gid, "\
                      "       date, "\
                      "       IF(quota=0, 0, ROUND((used / quota) * 100, 0)) "\
                      "         as ratio " \
                      "FROM %s " \
                      "WHERE date between '%s' AND '%s' " \
                      % (self._table, start_date, end_date)
    
                if groups:
                    sql += "AND gid IN (%s) " % str(groups).strip('[]')

                sql += 'GROUP BY gid, date'
    
                logging.debug(sql)
                cur.execute(sql)

                for item in cur.fetchall():

                    name = item[0]
                    date = item[1]
                    ratio = None

                    if item[2]:
                        ratio = int(item[2])

                    results.append(GroupDateValueItem(name, date, ratio))

                if not results:
                    raise RuntimeError("Found empty result list!")
    
        return results
