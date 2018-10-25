#!/usr/bin/env python
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

from contextlib import closing
from decimal import Decimal
from lfs.retrieve_quota import retrieve_group_quota


# TODO: Make Singleton Class?!

# Data structures are initialized on demand if necessary.
GROUP_NAMES_LIST = list()
GROUP_SIZES_LIST = list()
GROUP_QUOTA_DICT = dict()

CONFIG = None


class GroupNameItem:

    def __init__(self, gid, size):
        self.gid = gid


class GroupSizeItem:

    def __init__(self, gid, size):

        self.gid = gid
        self.size = Decimal(size)


class GroupQuotaItem:

    def __init__(self, gid, size):

        self.gid = gid
        self.size = Decimal(size)


class GroupInfoItem:

    def __init__(self, gid, size, quota):

        self.gid = gid
        self.size = Decimal(size)
        self.quota = Decimal(quota)


def get_group_names():

    global GROUP_NAMES_LIST

    if not GROUP_NAMES_LIST:

        rbh_acct_table = CONFIG.get('robinhood', 'acct_stat_table')

        with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                     user=CONFIG.get('mysqld', 'user'),
                                     passwd=CONFIG.get('mysqld', 'password'),
                                     db=CONFIG.get('robinhood', 'database'))) \
                as conn:

            with closing(conn.cursor()) as cur:

                sql = "SELECT DISTINCT gid FROM %s ORDER BY gid" \
                      % rbh_acct_table

                cur.execute(sql)

                if not cur.rowcount:
                    raise RuntimeError("No rows returned from query: %s" % sql)

                logging.debug("Initializing GROUP_NAMES_LIST ...")

                for gid in cur.fetchall():

                    logging.debug("Found GID: %s" % gid[0])

                    GROUP_NAMES_LIST.append(str(gid[0]))

    return GROUP_NAMES_LIST


def get_group_sizes():

    if not GROUP_SIZES_LIST:

        with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                     user=CONFIG.get('mysqld', 'user'),
                                     passwd=CONFIG.get('mysqld', 'password'),
                                     db=CONFIG.get('robinhood', 'database'))) \
                    as conn:

            with closing(conn.cursor()) as cur:

                sql = "SELECT gid, SUM(size) as group_size FROM %s " \
                      "GROUP BY gid ORDER BY group_size DESC" % \
                      (CONFIG.get('robinhood', 'acct_stat_table'))

                logging.debug(sql)
                cur.execute(sql)

                for item in cur.fetchall():
                    GROUP_SIZES_LIST.append(GroupSizeItem(item[0], item[1]))

                if not GROUP_SIZES_LIST:
                    raise RuntimeError("Empty GROUP_SIZES_LIST!")

    return GROUP_SIZES_LIST


def get_total_size():

    total_size = 0

    for group_size_item in get_group_sizes():
        total_size += group_size_item.size

    if not total_size:
        raise RuntimeError("Total Size is 0!")

    return total_size


def get_group_info_list():

    group_info_list = list()

    filesystem = CONFIG.get('lustre', 'filesystem')

    # TODO: Get quota for group list...
    for item in get_group_sizes():

        quota = None

        if item.gid in GROUP_QUOTA_DICT:
            quota = GROUP_QUOTA_DICT[item.gid]

        else:

            logging.debug("Retrieving Quota for GID: %s" % item.gid)

            quota = retrieve_group_quota(item.gid, filesystem)

            GROUP_QUOTA_DICT[item.gid] = quota

        if quota is None:
            raise RuntimeError('No quota retrieved for gid: %s' % item.gid)

        group_info_list.append(GroupInfoItem(item.gid, item.size, quota))

    if not group_info_list:
        raise RuntimeError('Empty group_info_list!')

    return group_info_list


def get_top_group_sizes():

    num_top_groups = int(CONFIG.get('base_chart', 'num_top_groups'))

    top_group_sizes_list = get_group_sizes()[:num_top_groups]

    if not top_group_sizes_list:
        raise RuntimeError('No top groups could be retrieved!')

    return top_group_sizes_list


def get_top_group_info_list():

    num_top_groups = int(CONFIG.get('base_chart', 'num_top_groups'))

    # TODO: Convinient but slow to call lfs on each group!
    # Better pass a group for retrieving lfs quota..
    top_group_info_list = get_group_info_list()[:num_top_groups]

    if not top_group_info_list:
        raise RuntimeError('No top groups could be retrieved!')

    return top_group_info_list


def calc_others_size(group_size_list, total_size):

    if not group_size_list:
        raise RuntimeError('group_size_list is not set or empty!')

    if not total_size:
        raise RuntimeError('Total size is not set or 0!')

    sum_group_size = 0

    for group_size_item in group_size_list:
        sum_group_size += group_size_item.size

    logging.debug("Sum of aggregated groups: %s" % sum_group_size)

    return total_size - sum_group_size
