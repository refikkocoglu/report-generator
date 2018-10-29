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


def get_group_sizes_list():

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


def get_groups_total_size():

    groups_total_size = 0

    for group_size_item in get_group_sizes_list():
        groups_total_size += group_size_item.size

    if not groups_total_size:
        raise RuntimeError("Total Size is 0!")

    return groups_total_size


def get_group_info_list():

    group_info_list = list()

    filesystem = CONFIG.get('lustre', 'filesystem')

    # TODO: Get quota for group list...
    for item in get_group_sizes_list():

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

    top_group_sizes_list = get_group_sizes_list()[:num_top_groups]

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
    group_info_list.append(GroupInfoItem('ufk', '5180489216282', '0'))
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
    group_info_list.append(GroupInfoItem('root', '790829819336', '0'))
    group_info_list.append(GroupInfoItem('thd', '346240925999', '0'))
    group_info_list.append(GroupInfoItem('rzgast', '133203420737', '0'))
    group_info_list.append(
        GroupInfoItem('hht', '130642827472', '21990232555520'))
    group_info_list.append(GroupInfoItem('ee', '58032178677', '0'))
    group_info_list.append(GroupInfoItem('su', '27676842674', '0'))
    group_info_list.append(
        GroupInfoItem('htit', '16930263228', '42949672960'))
    group_info_list.append(
        GroupInfoItem('psl', '12815424839', '107374182400'))
    group_info_list.append(
        GroupInfoItem('nustar', '5637091577', '107374182400'))
    group_info_list.append(GroupInfoItem('vw', '24472895', '576716800'))
    group_info_list.append(GroupInfoItem('staff', '3846924', '0'))
    group_info_list.append(GroupInfoItem('fat', '2265308', '0'))
    group_info_list.append(GroupInfoItem('997', '939808', '0'))
    group_info_list.append(GroupInfoItem('99', '764464', '0'))
    group_info_list.append(GroupInfoItem('81', '636848', '0'))
    group_info_list.append(GroupInfoItem('156', '441904', '0'))
    group_info_list.append(
        GroupInfoItem('astrum', '125315', '1099511627776'))
    group_info_list.append(GroupInfoItem('tty', '39072', '0'))
    group_info_list.append(GroupInfoItem('rzg-int', '23638', '0'))
    group_info_list.append(GroupInfoItem('utmp', '22384', '0'))
    group_info_list.append(GroupInfoItem('systemd-bus-proxy', '17346', '0'))
    group_info_list.append(GroupInfoItem('120', '12288', '0'))
    group_info_list.append(GroupInfoItem('man', '8192', '0'))
    group_info_list.append(GroupInfoItem('mail', '8192', '0'))
    group_info_list.append(GroupInfoItem('35', '8192', '0'))
    group_info_list.append(GroupInfoItem('bel', '4096', '10995116277760'))
    group_info_list.append(GroupInfoItem('adm', '1192', '0'))
    group_info_list.append(GroupInfoItem('fsr', '0', '576716800'))

    if number:
        return group_info_list[:number]
    else:
        return group_info_list