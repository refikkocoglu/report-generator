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


def get_group_names():

    group_names = list()

    rbh_acct_table = CONFIG.get('robinhood', 'acct_stat_table')

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

    acct_stat_table = CONFIG.get('robinhood', 'acct_stat_table')

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

    acct_stat_table = CONFIG.get('robinhood', 'acct_stat_table')

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

    filesystem = CONFIG.get('lustre', 'filesystem')

    for item in get_group_sizes(group_names):

        logging.debug("Retrieving Quota for Group: %s" % item.name)

        quota = retrieve_group_quota(item.name, filesystem)

        if quota is None:
            raise RuntimeError('No quota retrieved for Group: %s' % item.name)

        group_info_list.append(GroupInfoItem(item.name, item.size, quota))

    if not group_info_list:
        raise RuntimeError('Empty group_info_list!')

    return group_info_list


def get_top_group_sizes():

    acct_stat_table = CONFIG.get('robinhood', 'acct_stat_table')
    num_top_groups = int(CONFIG.get('base_chart', 'num_top_groups'))

    top_group_sizes = list()

    with closing(MySQLdb.connect(host=CONFIG.get('mysqld', 'host'),
                                 user=CONFIG.get('mysqld', 'user'),
                                 passwd=CONFIG.get('mysqld', 'password'),
                                 db=CONFIG.get('robinhood', 'database'))) \
            as conn:

        with closing(conn.cursor()) as cur:

            sql = "SELECT gid, SUM(size) as group_size FROM %s " \
                  "GROUP BY gid ORDER BY group_size DESC LIMIT %s" % \
                  (acct_stat_table, num_top_groups)

            logging.debug(sql)
            cur.execute(sql)

            for item in cur.fetchall():
                top_group_sizes.append(GroupSizeItem(item[0], item[1]))

            if not top_group_sizes:
                raise RuntimeError("Empty Group Sizes List!")

    return top_group_sizes


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


def sort_group_info_list_by_quota(group_info_list):
    """
    Inplace sort of the given group_info_list in descending order by quota.
    """

    group_info_list.sort(key=lambda group_info: group_info.quota, reverse=True)


def sort_group_info_list_by_name(group_info_list):
    """
    Inplace sort of the given group_info_list in ascending order by name.
    """

    group_info_list.sort(key=lambda group_info: group_info.name)
