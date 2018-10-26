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


import numpy as np
import matplotlib.pyplot as plt
import dataset.dataset_handler as ds


def draw(group_info_list):

    num_groups = len(group_info_list)

    group_names = list()
    quota_used_pct_list = list()

    for group_info in group_info_list:

        group_names.append(group_info.gid)

        if group_info.quota and group_info.size:
            quota_used_pct = round((group_info.size / group_info.quota) * 100)

        else:
            quota_used_pct = 0

        quota_used_pct_list.append(quota_used_pct)
    
    ind = np.arange(num_groups)  # the x locations for the groups

    bar_width = 0.35  # the width of the bars: can also be len(x) sequence

    fig_width = num_groups
    fig_height = 10.0

    plt.figure(figsize=(fig_width, fig_height))

    plt.bar(ind, quota_used_pct_list, bar_width, color='blue')

    plt.title('Group Quota Usage of Lustre Nyx')
    plt.xlabel('Group')
    plt.ylabel('Quota Usage (%)')

    plt.xticks(ind, group_names)
    plt.yticks(np.arange(0, 101, 10))

    x = np.linspace(0, num_groups)
    y = np.linspace(100, 100)

    plt.plot(x, y, linewidth=0.8, color='red', linestyle='dashed',
             label='Quota Limit')

    plt.legend()


def create_bar_chart_dev(file_path, num_groups=None):

    group_info_list = ds.create_dummy_group_info_list(num_groups)

    draw(group_info_list)

    plt.savefig(file_path, format='svg', dpi=300)

    plt.show()
