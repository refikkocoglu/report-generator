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

import numpy as np
import logging
import datetime
import os

# TODO: Check imports into base class...
# Force matplotlib to not use any X window backend.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class QuotaUsageChart(BaseChart):

    def __init__(self, title='', sub_title='', file_path='', dataset=None):

        x_label = 'Group'
        y_label = 'Quota Usage (%)'

        super(QuotaUsageChart, self).__init__(title,
                                              x_label, y_label,
                                              file_path, dataset)

        self.sub_title = 'Procedural Usage per Group'

    def _draw(self):

        num_groups = len(self.dataset)

        logging.debug("Number of Groups: %s" % num_groups)

        self._sort_dataset(lambda group_info: group_info.name)

        group_names = list()
        quota_used_pct_list = list()

        for group_info in self.dataset:

            group_names.append(group_info.name)

            if group_info.quota and group_info.size:
                quota_used_pct = \
                    round((group_info.size / group_info.quota) * 100)

            else:
                quota_used_pct = 0

            quota_used_pct_list.append(quota_used_pct)

        ind = np.arange(num_groups)  # the x locations for the groups

        bar_width = 0.35  # the width of the bars: can also be len(x) sequence

        fig_width = num_groups
        fig_height = 10.0

        self._fig = plt.figure(figsize=(fig_width, fig_height))

        self._fig.suptitle(self.title, fontsize=18, fontweight='bold')
        self._fig.subplots_adjust(top=0.80)

        plt.bar(ind, quota_used_pct_list, bar_width, color='blue')

        plt.title(self.sub_title)

        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)

        plt.xticks(ind, group_names)
        plt.yticks(np.arange(0, 101, 10))

        x = np.linspace(0, num_groups)
        y = np.linspace(100, 100)

        plt.plot(x, y,
                 linewidth=0.8, linestyle='dashed',
                 label='Quota Limit', color='red')

        plt.legend()

    @staticmethod
    def _sorted_group_info_list(group_info_list, sort_key):
        return sorted(group_info_list, key=sort_key)
