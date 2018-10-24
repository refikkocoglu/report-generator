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


class GroupInfo:

    def __init__(self, gid, size, count):
        self.gid = gid
        self.size = size
        self.count = count


def get_total_size(config):

    with closing(MySQLdb.connect(host=config.get('mysqld', 'host'),
                                 user=config.get('mysqld', 'user'),
                                 passwd=config.get('mysqld', 'password'),
                                 db=config.get('robinhood', 'database'))) \
            as conn:

        with closing(conn.cursor()) as cur:

            sql = "SELECT SUM(size) FROM %s" % config.get('robinhood', 'acct_stat_table')
            logging.debug(sql)
            cur.execute(sql)

            total_size = cur.fetchone()[0]

            if not cur.rowcount or not total_size:
                raise RuntimeError('Failed to retrieve total sum for size from accounting table!')

            return total_size


def get_top_group_list(config):

    with closing(MySQLdb.connect(host=config.get('mysqld', 'host'),
                                 user=config.get('mysqld', 'user'),
                                 passwd=config.get('mysqld', 'password'),
                                 db=config.get('robinhood', 'database'))) \
                as conn:

        with closing(conn.cursor()) as cur:

            sql = "SELECT gid, SUM(size) as group_size FROM %s GROUP BY gid ORDER BY group_size DESC LIMIT %s" % \
                  (config.get('robinhood', 'acct_stat_table'), config.get('pie_chart_disk_used', 'num_top_groups'))

            logging.debug(sql)
            cur.execute(sql)

            group_by_size_list = cur.fetchall()
            group_info_list = list()

            if not cur.rowcount or not group_by_size_list:
                raise RuntimeError(
                    'Failed to retrieve group by size list from accounting table!')

            for group_entry in group_by_size_list:
                group_info_list.append(GroupInfo(group_entry[0], group_entry[1], 0))

            return group_info_list


def calc_others_size(group_info_list, total_size):

    group_size = 0

    for group_info in group_info_list:
        group_size += group_info.size

    logging.debug("Total size of aggregated groups: %s" % group_size)

    return total_size - group_size