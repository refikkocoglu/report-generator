#!/usr/bin/env python3
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


from base_chart import BaseChart

import numpy as np
from format import number_format

import matplotlib
# Force matplotlib to not use any X window backend.
matplotlib.use('Agg')


class UsageQuotaBarChart(BaseChart):

    def __init__(self, title, dataset, file_path):

        super(UsageQuotaBarChart, self).__init__(title, dataset, file_path,
                                                 x_label='Group',
                                                 y_label='Disk Space / Quota Used (TiB)')
    
    def _draw(self):
        
        num_groups = len(self.dataset)
        
        self._sort_dataset(
            key=lambda group_info: group_info.quota, reverse=True)
        
        tick_width_y = 200
        
        max_y = float(self.dataset[0].quota /
                      number_format.TIB_DIVISIOR) + tick_width_y

        group_names = list()
        quota_list_values = list()
        size_list_values = list()

        for group_info in self.dataset:

            group_names.append(group_info.name)

            quota_list_values.append(
                int(group_info.quota / number_format.TIB_DIVISIOR))

            size_list_values.append(
                int(group_info.size / number_format.TIB_DIVISIOR))

        ind = np.arange(num_groups)  # The x locations for the groups

        bar_width = 0.35  # the width of the bars: can also be len(x) sequence

        p1 = self._ax.bar(ind, size_list_values, bar_width, color='blue')

        p2 = self._ax.bar(ind + bar_width, quota_list_values,
                          bar_width, color='orange')

        self._ax.set_xticks(ind + bar_width / 2)
        self._ax.set_xticklabels(group_names, rotation=45)

        self._ax.set_yticks(np.arange(0, max_y, tick_width_y))

        self._ax.legend((p2[0], p1[0]), ('Quota', 'Used'))
