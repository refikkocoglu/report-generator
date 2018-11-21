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


import MySQLdb
import logging
import datetime

from contextlib import closing
from decimal import Decimal
from lfs.retrieve_quota import retrieve_group_quota


# TODO:
# DATASOURCE SHOULD NOT KNOW ANYTHING ABOUT TOP GROUPS!!!
# JUST PROVIDE GROUP INFORMATION AND RETURN NUMBER OF GROUP ITEMS!!!


# TODO: Make Singleton Class?!

CONFIG = None


class GroupSizeItem:

    def __init__(self, name, size):

        self.name = name
        self.size = Decimal(size)


class GroupInfoItem:

    def __init__(self, name, size, quota):

        self.name = name
        self.size = Decimal(size)
        self.quota = Decimal(quota)


class GroupDateValueItem:

    def __init__(self, name, date, value):

        self.name = name

        # TODO: Convertion to date???
        self.date = date

        if value:
            self.value = int(value)
        else:
            self.value = None


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
    :return: A list of GroupDateSizeItem.
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
                result_list.append(
                    GroupDateValueItem(item[0], item[1], item[2]))

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
                result_list.append(
                    GroupDateValueItem(item[0], item[1], item[2]))

            if not result_list:
                raise RuntimeError("Found empty result list!")

    return result_list


def create_dummy_group_info_list(number=None):

    group_info_list = list()

    group_info_list.append(
        GroupInfoItem('asteg', '2612725871277742', '2748779069440000'))
    group_info_list.append(
        GroupInfoItem('alidata', '1984900832193635', '2035196023013376'))
    group_info_list.append(
        GroupInfoItem('hades', '1508392669128129', '1564605046325248'))
    group_info_list.append(
        GroupInfoItem('alice', '1077588550802481', '1319413953331200'))
    group_info_list.append(
        GroupInfoItem('fn', '1022718464634783', '945579999887360'))
    group_info_list.append(
        GroupInfoItem('cbm', '738440430421761', '1209462790553600'))
    group_info_list.append(
        GroupInfoItem('pbar', '375407152760683', '945579999887360'))
    group_info_list.append(
        GroupInfoItem('afseg', '269953044185563', '659706976665600'))
    group_info_list.append(
        GroupInfoItem('land', '114726018555229', '164926744166400'))
    group_info_list.append(
        GroupInfoItem('hyihp', '110467581455500', '142936511610880'))
    group_info_list.append(
        GroupInfoItem('fopi', '106306847077093', '115448720916480'))
    group_info_list.append(
        GroupInfoItem('fltc', '105399288025433', '126443837194240'))
    group_info_list.append(
        GroupInfoItem('ks', '72702387970910', '87960930222080'))
    group_info_list.append(
        GroupInfoItem('tasca', '70261949736621', '71468255805440'))
    group_info_list.append(
        GroupInfoItem('the', '63971130556753', '103354093010944'))
    group_info_list.append(
        GroupInfoItem('ap', '55192157271191', '65970697666560'))
    group_info_list.append(
        GroupInfoItem('had1', '52089033367758', '87960930222080'))
    group_info_list.append(
        GroupInfoItem('bio', '45139228432740', '82463372083200'))
    group_info_list.append(
        GroupInfoItem('alitrain', '39386206628620', '109951162777600'))
    group_info_list.append(
        GroupInfoItem('hij', '29268878252590', '38482906972160'))
    group_info_list.append(
        GroupInfoItem('kc', '17347387740312', '18691697672192'))
    group_info_list.append(
        GroupInfoItem('ukt', '14338270055031', '49478023249920'))
    group_info_list.append(
        GroupInfoItem('uf7', '11561779120430', '76965813944320'))
    group_info_list.append(
        GroupInfoItem('kr', '8886451453013', '17592186044416'))
    group_info_list.append(
        GroupInfoItem('him', '6798995223478', '26388279066624'))
    group_info_list.append(
        GroupInfoItem('rz', '6687087233272', '10995116277760'))
    group_info_list.append(
        GroupInfoItem('tpcdata', '6090686094889', '27487790694400'))
    group_info_list.append(
        GroupInfoItem('kp2', '6086615963545', '6873068560384'))
    group_info_list.append(
        GroupInfoItem('ul', '5157645070220', '6597069766656'))
    group_info_list.append(
        GroupInfoItem('bhs', '4822637002137', '32985348833280'))
    group_info_list.append(
        GroupInfoItem('hpc', '4555805045551', '25288767438848'))
    group_info_list.append(
        GroupInfoItem('hyphi', '3468981480003', '4509715660800'))
    group_info_list.append(
        GroupInfoItem('kp1', '2833990585812', '2914135310336'))
    group_info_list.append(
        GroupInfoItem('fairgsi', '2440403339127', '5497558138880'))
    group_info_list.append(
        GroupInfoItem('radprot', '2181051911650', '76965813944320'))
    group_info_list.append(
        GroupInfoItem('hht', '130642827472', '21990232555520'))
    group_info_list.append(
        GroupInfoItem('htit', '16930263228', '42949672960'))
    group_info_list.append(
        GroupInfoItem('psl', '12815424839', '107374182400'))
    group_info_list.append(
        GroupInfoItem('nustar', '5637091577', '107374182400'))
    group_info_list.append(GroupInfoItem('vw', '24472895', '576716800'))
    group_info_list.append(
        GroupInfoItem('astrum', '125315', '1099511627776'))
    group_info_list.append(GroupInfoItem('bel', '4096', '10995116277760'))

    if number:
        return group_info_list[:number]
    else:
        return group_info_list


def create_dummy_group_date_values(num_groups=3, max_value=100):
    """
        Date interval is from 2018-12-01 to 2018-12-31.
        :param num_groups: Specifies number of groups.
        :param max_value: Specifies maximum value in value range.
        :return: A list of GroupDataSizeItems.
    """

    import random

    group_date_size_item_list = list()

    for day in range(1, 31+1):

        for gid in range(num_groups):

            # Data formatting could be that way...
            # date_format = '%Y-%m-%d'
            # datetime.datetime.strptime(date, date_format).date()

            group = "group%s" % gid
            date = "2018-12-%s" % day
            value = random.randint(1, max_value)

            group_date_size_item_list.append(
                GroupDateValueItem(group, date, value))

    return group_date_size_item_list
