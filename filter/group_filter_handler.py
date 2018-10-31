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

import logging
import getent


GID_CACHE_DICT = dict()


def filter_system_groups(group_list):
    """
    Filters system groups from given list.
    :param group_list: Group list which should at least contain field gid.
    :return: A new list without system groups.
    """

    #TODO: Check base Class for GroupItem or something that the object have at least the gid in the strucutre!

    non_system_group_list = list()

    for group_item in group_list:

        group_id = None

        if group_item.name in GID_CACHE_DICT:
            group_id = GID_CACHE_DICT[group_item.name]
        else:

            group_info = getent.group(group_item.name)

            if group_info is not None:

                GID_CACHE_DICT[group_item.name] = group_info.gid

                group_id = group_info.gid

            else:
                group_id = None

        if group_id is not None and group_id > 999:

            non_system_group_list.append(group_item)

            logging.debug("Found non-system GID: %s for Group: %s" %
                          (group_id, group_item.name))

        else:
            logging.debug("Ignoring System Group: %s" % group_item.name)

    return non_system_group_list


def filter_group_info_items(group_info_list, size=0, quota=0):

    new_group_info_list = list()

    if group_info_list is None or len(group_info_list) == 0:
        raise RuntimeError("Empty group_info_list found!")

    for group_info_item in group_info_list:

        # TODO: Check list if contains instances of GorupInfoItem class.

        if group_info_item.size <= size and group_info_item.quota <= quota:
            logging.debug("Filtered group_info_item for group: %s"
                          % group_info_item.name)
            continue

        new_group_info_list.append(group_info_item)

    return new_group_info_list
