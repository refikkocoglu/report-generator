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


from dataset.dataset_handler import get_top_group_list
from lfs.retrieve_quota import retrieve_group_quota


def create_stacked_bar(config):

    filesystem = config.get('lustre', 'filesystem')

    group_info_list = get_top_group_list(config)

    for group_info in group_info_list:

        print "gid: %s - quota: %s" % \
              (group_info.gid, retrieve_group_quota(group_info.gid, filesystem))

