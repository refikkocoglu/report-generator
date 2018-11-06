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

import os
import datetime
import format.number_format as nf
import dataset.dataset_handler as ds

from decimal import Decimal
from lfs import disk_usage_info

# TODO: Check imports into base class...
# Force matplotlib to not use any X window backend.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class DiskUsageChart(BaseChart):

    def __init__(self, title='', file_path='', dataset=None,
                 storage_total_size=0, num_top_groups=8):

        x_label = 'Group'
        y_label = 'Quota Usage (%)'

        super(DiskUsageChart, self).__init__(title, x_label, y_label,
                                             file_path, dataset)

        self.num_top_groups = num_top_groups

        self.storage_total_size = storage_total_size

    def _draw(self):

        labels = []
        sizes = []

        self._sort_dataset(lambda group_info: group_info.size, True)

        top_groups_info_list = self.dataset[:self.num_top_groups]

        groups_total_size = \
            DiskUsageChart._calc_groups_total_size(self.dataset)

        top_groups_total_size = \
            DiskUsageChart._calc_groups_total_size(top_groups_info_list)

        others_size = groups_total_size - top_groups_total_size

        for item in top_groups_info_list:

            label_text = item.name + " (" + nf.number_to_base_2(item.size) + ")"

            labels.append(label_text)
            sizes.append(item.size)

        labels.append("others (" + nf.number_to_base_2(others_size) + ")")
        sizes.append(others_size)

        self._fig, ax = plt.subplots()

        self._fig.suptitle(self.title, fontsize=18, fontweight='bold')
        self._fig.subplots_adjust(top=0.80)

        patches, texts, auto_texts = \
            ax.pie(sizes, labels=labels, autopct='%1.2f%%', pctdistance=0.8,
                   shadow=False, startangle=90)

        # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.axis('equal')

        for auto_text_item in auto_texts:
            auto_text_item.set_fontsize(10)

        total_size_pct_used = \
            int((groups_total_size / self.storage_total_size) * Decimal(100))

        sub_title = "Used " + nf.number_to_base_2(groups_total_size) + \
                    " of " + nf.number_to_base_2(self.storage_total_size) + \
                    " Volume (" + str(total_size_pct_used) + "%)"

        ax.set_title(sub_title, y=1.125, fontsize=14)

        self._add_creation_text(ax)

        self._fig.set_size_inches(10, 8)

    def _add_creation_text(self, ax):

        ax.text(0, 0, datetime.datetime.now().strftime('%Y-%m-%d - %X'),
                verticalalignment='bottom', horizontalalignment='left',
                fontsize=8, transform=self._fig.transFigure)

    @staticmethod
    def _calc_groups_total_size(group_info_list):

        groups_total_size = 0

        for group_info_item in group_info_list:
            groups_total_size += group_info_item.size

        return groups_total_size
