#!/usr/bin/env python3
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


import datetime

from decimal import Decimal


class GroupInfoItem:

    def __init__(self, name, size=0, quota=0, files=0):

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

        if type(name) != str:
            raise RuntimeError("Parameter name is not a string!")

        if type(date) != datetime.date:
            raise RuntimeError("Parameter date is not a datetime.date!")

        self.name = name
        self.date = date
        self.value = value


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
        GroupInfoItem('group1', '2612725871277742', '2748779069440000'))
    group_info_list.append(
        GroupInfoItem('group2', '1984900832193635', '2035196023013376'))
    group_info_list.append(
        GroupInfoItem('group3', '1508392669128129', '1564605046325248'))
    group_info_list.append(
        GroupInfoItem('group4', '1077588550802481', '1319413953331200'))
    group_info_list.append(
        GroupInfoItem('group5', '1022718464634783', '945579999887360'))
    group_info_list.append(
        GroupInfoItem('group6', '738440430421761', '1209462790553600'))
    group_info_list.append(
        GroupInfoItem('group7', '375407152760683', '945579999887360'))
    group_info_list.append(
        GroupInfoItem('group8', '269953044185563', '659706976665600'))
    group_info_list.append(
        GroupInfoItem('group9', '114726018555229', '164926744166400'))
    group_info_list.append(
        GroupInfoItem('group10', '110467581455500', '142936511610880'))
    group_info_list.append(
        GroupInfoItem('group11', '106306847077093', '115448720916480'))
    group_info_list.append(
        GroupInfoItem('group12', '105399288025433', '126443837194240'))
    group_info_list.append(
        GroupInfoItem('group13', '72702387970910', '87960930222080'))
    group_info_list.append(
        GroupInfoItem('group14', '70261949736621', '71468255805440'))
    group_info_list.append(
        GroupInfoItem('group15', '63971130556753', '103354093010944'))
    group_info_list.append(
        GroupInfoItem('group16', '55192157271191', '65970697666560'))
    group_info_list.append(
        GroupInfoItem('group17', '52089033367758', '87960930222080'))
    group_info_list.append(
        GroupInfoItem('group18', '45139228432740', '82463372083200'))
    group_info_list.append(
        GroupInfoItem('group19', '39386206628620', '109951162777600'))
    group_info_list.append(
        GroupInfoItem('group20', '29268878252590', '38482906972160'))

    if number:
        return group_info_list[:number]
    else:
        return group_info_list


def create_dummy_group_date_values(num_groups=3, max_value=100, start_date, 
        start_date='2018-12-01', end_date='2018-12-31'):
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

            group = "group%s" % gid

            new_date = "2018-12-%s" % day
            date = datetime.datetime.strptime(new_date, '%Y-%m-%d').date()

            value = random.randint(1, max_value)

            group_date_size_item_list.append(
                GroupDateValueItem(group, date, value))

    return group_date_size_item_list


def create_dummy_group_files_migration_info_list():

    group_info_list = list()

    group_info_list.append(
        GroupFilesMigrationInfoItem('group1', '36022092', '34022092'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('group2', '22634135', '20634135'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('group3', '34974617', '30074617'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('group4', '292229284', '202229284'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('group5', '1396443', '1096443'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('group6', '50536512', '50036512'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('group7', '27008494', '20888494'))
    group_info_list.append(
        GroupFilesMigrationInfoItem('group8', '1102831', '1160031'))

    return group_info_list
