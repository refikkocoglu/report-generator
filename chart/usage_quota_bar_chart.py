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


from base_chart import BaseChart

import logging
import numpy as np
from format import number_format

# Force matplotlib to not use any X window backend.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class UsageQuotaBarChart(BaseChart):

    def __init__(self, title='', sub_title='', file_path='', dataset=None):

        x_label = 'Group'
        y_label = 'Disk Space Used (TiB)'

        super(UsageQuotaBarChart, self).__init__(title, sub_title,
                                                 x_label, y_label,
                                                 file_path, dataset)

    def _draw(self):

        num_groups = len(self.dataset)

        logging.debug("Number of Groups: %s" % num_groups)

        self._sort_dataset(
            key=lambda group_info: group_info.quota, reverse=True)

        group_names = list()
        quota_list_values = list()
        size_list_values = list()

        tick_width_y = 200

        max_y = float(self.dataset[0].quota /
                      number_format.TIB_DIVISIOR) + tick_width_y

        for group_info in self.dataset:
            logging.debug("%s - %s - %s" % (
                group_info.name, group_info.size, group_info.quota))

            group_names.append(group_info.name)

            quota_list_values.append(
                int(group_info.quota / number_format.TIB_DIVISIOR))

            size_list_values.append(
                int(group_info.size / number_format.TIB_DIVISIOR))

        ind = np.arange(num_groups)  # the x locations for the groups

        bar_width = 0.35  # the width of the bars: can also be len(x) sequence

        fig_width = num_groups
        fig_height = 10.0

        self._fig = plt.figure(figsize=(fig_width, fig_height))

        self._fig.suptitle(self.title, fontsize=18, fontweight='bold')
        plt.title(self.sub_title)

        p1 = plt.bar(ind, size_list_values, bar_width, color='blue')
        p2 = plt.bar(ind + bar_width, quota_list_values, bar_width, color='orange')

        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)

        plt.xticks(ind + bar_width / 2, group_names)

        plt.yticks(np.arange(0, max_y, tick_width_y))
        plt.legend((p2[0], p1[0]), ('Quota', 'Used'))

        self._add_creation_text()
