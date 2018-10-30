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


import getent
import logging


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

        if group_item.gid in GID_CACHE_DICT:
            group_id = GID_CACHE_DICT[group_item.gid]
        else:

            group_info = getent.group(group_item.gid)

            if group_info:

                GID_CACHE_DICT[group_item.gid] = group_info.gid

                group_id = group_info.gid

            else:

                group_id = None

        if group_id and group_id > 999:

            non_system_group_list.append(group_item)

            logging.debug("Found GID: %s for Group: %s" %
                          (group_id, group_item.gid))

        else:
            logging.debug("Ignoring System Group: %s" % group_item.gid)

    return non_system_group_list

