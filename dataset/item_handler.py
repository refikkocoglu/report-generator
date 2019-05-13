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


from decimal import Decimal


# TODO: Remove "Group" prefix to use it later for user as well...
#       e.g. SizeItem, GroupItem, ...
# -> Refactor to one InfoItem class with default parameter!
# But requires code changes to each object creater and caller.
# HOW ABOUT CONSTRUCTOR OVERLOADING IN PYTHON???
# OTHERWISE create the proper create funtions, no bad design!
# BETTER set at least the quota=0 and files=0 so it is opional!

class GroupSizeItem:

    def __init__(self, name, size):

        self.name = name
        self.size = Decimal(size)


class GroupInfoItem:

    def __init__(self, name, size, quota):

        self.name = name
        self.size = Decimal(size)
        self.quota = Decimal(quota)


class GroupFullInfoItem:

    def __init__(self, name, size, quota, files):

        self.name = name
        self.size = Decimal(size)
        self.quota = Decimal(quota)
        self.files = Decimal(files)


class GroupFilesMigrationInfoItem:

    def __init__(self, name, fs1_file_count, fs2_file_count):

        self.name = name
        self.fs1_file_count = Decimal(fs1_file_count)
        self.fs2_file_count = Decimal(fs2_file_count)


class GroupDateValueItem:

    def __init__(self, name, date, value):

        self.name = name

        # TODO: Convertion to date???
        self.date = date

        if value:
            self.value = int(value)
        else:
            self.value = None


def create_group_date_value_item_dict(group_date_value_item_list):

    item_dict = dict()

    for item in group_date_value_item_list:

        # TODO: Optimize by cached 'group_item_dict[group_item.name]' key object.
        if item.name in item_dict:

            item_dict[item.name][0].append(item.date)
            item_dict[item.name][1].append(item.value)

        else:

            item_dict[item.name] = (list(), list())

            item_dict[item.name][0].append(item.date)
            item_dict[item.name][1].append(item.value)

    return item_dict


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
    group_info_list.append(
        GroupInfoItem('vw', '24472895', '576716800'))
    group_info_list.append(
        GroupInfoItem('astrum', '125315', '1099511627776'))
    group_info_list.append(
        GroupInfoItem('bel', '4096', '10995116277760'))

    if number:
        return group_info_list[:number]
    else:
        return group_info_list


def create_dummy_group_date_values(num_groups=3, max_value=100):
    """
        Date interval is from 2018-12-01 to 2018-12-31.
        :param num_groups: Specifies number of groups.
        :param max_value: Specifies maximum value in value range.
        :return: A list of GroupDateValueItem.
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


def create_dummy_group_files_migration_info_list():

    group_info_list = list()

    group_info_list.append(
        GroupFilesMigrationInfoItem('asteg', '36022092', '34022092'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('alidata', '22634135', '20634135'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('hades', '34974617', '30074617'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('alice', '292229284', '202229284'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('fn', '1396443', '1096443'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('cbm', '50536512', '50036512'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('pbar', '27008494', '20888494'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('afseg', '1102831', '1160031'))

    return group_info_list
