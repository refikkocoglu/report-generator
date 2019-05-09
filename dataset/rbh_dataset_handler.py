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

from dataset.lfs_dataset_handler import retrieve_group_quota
from dataset.item_handler import GroupSizeItem, GroupInfoItem, GroupDateValueItem


# TODO: Make Singleton Class?!

CONFIG = None


def get_group_names():

    group_names = list()

    rbh_acct_table = CONFIG.get('robinhood', 'table')

    with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                 user=CONFIG.get('mysqld', 'user'),
                                 passwd=CONFIG.get('mysqld', 'password'),
                                 db=CONFIG.get('robinhood', 'database'))) \
            as conn:

        with closing(conn.cursor()) as cur:

            sql = "SELECT DISTINCT gid FROM %s ORDER BY gid" % rbh_acct_table

            cur.execute(sql)

            if not cur.rowcount:
                raise RuntimeError("No rows returned from query: %s" % sql)

            for group_name in cur.fetchall():

                logging.debug("Retrieved Group Name: %s" % group_name[0])

                group_names.append(str(group_name[0]))

    return group_names


def get_group_sizes(group_names):

    group_sizes = list()

    acct_stat_table = CONFIG.get('robinhood', 'table')

    with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                 user=CONFIG.get('mysqld', 'user'),
                                 passwd=CONFIG.get('mysqld', 'password'),
                                 db=CONFIG.get('robinhood', 'database'))) \
            as conn:

        with closing(conn.cursor()) as cur:

            group_names_string = str(group_names).strip('[]')

            sql = "SELECT gid, SUM(size) FROM %s WHERE gid IN (%s) " \
                  "GROUP BY gid" % (acct_stat_table, group_names_string)

            logging.debug(sql)
            cur.execute(sql)

            for item in cur.fetchall():
                group_sizes.append(GroupSizeItem(item[0], item[1]))

            if not group_sizes:
                raise RuntimeError("Empty Group Sizes List!")

    return group_sizes


def get_groups_total_size():

    total_size = None

    acct_stat_table = CONFIG.get('robinhood', 'table')

    with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                 user=CONFIG.get('mysqld', 'user'),
                                 passwd=CONFIG.get('mysqld', 'password'),
                                 db=CONFIG.get('robinhood', 'database'))) \
            as conn:

        with closing(conn.cursor()) as cur:

            sql = "SELECT SUM(size) FROM %s" % acct_stat_table

            logging.debug(sql)
            cur.execute(sql)

            total_size = cur.fetchone()[0]

    if total_size is None:
        raise RuntimeError("Total Size was not retrieved from Database!")

    if total_size == 0:
        raise RuntimeError("Total Size is 0!")

    return total_size


def get_group_info_list(group_names):

    group_info_list = list()

    filesystem = CONFIG.get('storage', 'filesystem')

    for item in get_group_sizes(group_names):

        logging.debug("Retrieving Quota for Group: %s" % item.name)

        quota = retrieve_group_quota(item.name, filesystem)

        if quota is None:
            raise RuntimeError('No quota retrieved for Group: %s' % item.name)

        group_info_list.append(GroupInfoItem(item.name, item.size, quota))

    if not group_info_list:
        raise RuntimeError('Empty group_info_list!')

    return group_info_list


def get_top_groups(limit):

    acct_stat_table = CONFIG.get('robinhood', 'table')

    grp_names_list = list()

    with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                 user=CONFIG.get('mysqld', 'user'),
                                 passwd=CONFIG.get('mysqld', 'password'),
                                 db=CONFIG.get('robinhood', 'database'))) \
            as conn:

        with closing(conn.cursor()) as cur:

            sql = "SELECT T.gid FROM " \
                  "(SELECT gid, SUM(size) as group_size FROM %s " \
                  "GROUP BY gid ORDER BY group_size DESC) AS T LIMIT %s" \
                  % (acct_stat_table, limit)

            logging.debug(sql)
            cur.execute(sql)

            for grp_name in cur.fetchall():
                grp_names_list.append(grp_name[0])

            if not grp_names_list:
                raise RuntimeError("Empty group list found!")

    return grp_names_list


def filter_groups_at_threshold_size(start_date, end_date, threshold,
                                    group_names=None):
    """
    Returns a list of group names that reached a certain threshold at size.
    :param start_date: Specifies the start date.
    :param end_date: Specifies the end date.
    :param threshold: Specifies the threshold for the size of groups.
    :param group_names: Specifies the group names to filter for.
    :return: A list of group names.
    """

    result_list = list()

    table = CONFIG.get('report', 'acct_table')

    with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                 user=CONFIG.get('mysqld', 'user'),
                                 passwd=CONFIG.get('mysqld', 'password'),
                                 db=CONFIG.get('report', 'database'))) \
            as conn:

        with closing(conn.cursor()) as cur:

            sql = "SELECT DISTINCT(gid) " \
                  "FROM ( " \
                  "SELECT gid, date, SUM(size) AS sum_size " \
                  "FROM %s " \
                  "WHERE date BETWEEN '%s' AND '%s' " \
                  % (table, start_date, end_date)

            if group_names:
                sql += " AND gid IN (%s) " % str(group_names).strip('[]')

            sql += "GROUP BY gid, date HAVING(sum_size >= %s) ) AS tmp_table" \
                   % threshold

            logging.debug(sql)
            cur.execute(sql)

            for item in cur.fetchall():
                result_list.append(item[0])

    return result_list


def get_time_series_group_sizes(start_date, end_date, group_names=None):
    """
    Queries ACCT_STAT_HISTORY table for given group names
    within a specific time interval filled with size consumption per day.
    The size consumption is saved on base of TiB.
    :param group_names: List of group names (optional).
    :param start_date: Start date of the time interval.
    :param end_date: End date of the time interval.
    :return: A list of GroupDateValueItem.
    """

    result_list = list()

    table = CONFIG.get('report', 'acct_table')

    with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                 user=CONFIG.get('mysqld', 'user'),
                                 passwd=CONFIG.get('mysqld', 'password'),
                                 db=CONFIG.get('report', 'database'))) \
            as conn:

        with closing(conn.cursor()) as cur:

            # TiB Divisor = '1099511627776'
            sql = "SELECT gid, date, ROUND(SUM(size)/1099511627776) as size " \
                  "FROM %s WHERE date between '%s' AND '%s'" \
                  % (table, start_date, end_date)

            if group_names:
                sql += " AND gid IN (%s)" % str(group_names).strip('[]')

            sql += ' GROUP BY gid, date'

            logging.debug(sql)
            cur.execute(sql)

            for item in cur.fetchall():
                result_list.append(GroupDateValueItem(item[0], item[1], item[2]))

            if not result_list:
                raise RuntimeError("Found empty result list!")

    return result_list


def get_time_series_group_quota_usage(start_date, end_date, group_names=None):
    """
    Queries ACCT_STAT- and QUOTA-History table for given group names
    within a specific time interval for quota consumption in percentage.
    :param group_names: List of group names (optional).
    :param start_date: Start date of the time interval.
    :param end_date: End date of the time interval.
    :return: A list of GroupDateValueItem.
    """

    result_list = list()

    acct_table = CONFIG.get('report', 'acct_table')
    quota_table = CONFIG.get('report', 'quota_table')

    with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                 user=CONFIG.get('mysqld', 'user'),
                                 passwd=CONFIG.get('mysqld', 'password'),
                                 db=CONFIG.get('report', 'database'))) \
            as conn:

        with closing(conn.cursor()) as cur:

            sql = "SELECT gid, date, ROUND((SUM(size) / quota) * 100, 0) " \
                  "FROM %s JOIN %s USING(gid, date) " \
                  "WHERE date between '%s' AND '%s'" \
                  % (acct_table, quota_table, start_date, end_date)

            if group_names:
                sql += " AND gid IN (%s)" % str(group_names).strip('[]')

            sql += ' GROUP BY gid, date'

            logging.debug(sql)
            cur.execute(sql)

            for item in cur.fetchall():
                result_list.append(GroupDateValueItem(item[0], item[1], item[2]))

            if not result_list:
                raise RuntimeError("Found empty result list!")

    return result_list
