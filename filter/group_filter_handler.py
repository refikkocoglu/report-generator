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

import logging


# TODO: Check list if contains instances of GorupInfoItem class.
def filter_group_info_items(group_info_list, size=0, quota=0):

    new_group_info_list = list()

    if group_info_list is None or len(group_info_list) == 0:
        raise RuntimeError("Empty group_info_list found!")

    for group_info_item in group_info_list:

        if group_info_item.size <= size and group_info_item.quota <= quota:

            logging.debug("Filtered group_info_item for group: %s"
                          % group_info_item.name)

        else:
            new_group_info_list.append(group_info_item)

    return new_group_info_list
