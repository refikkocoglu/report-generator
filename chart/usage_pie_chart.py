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

import format.number_format as nf
from decimal import Decimal

import matplotlib
# Force matplotlib to not use any X window backend.
matplotlib.use('Agg')


class UsagePieChart(BaseChart):

    def __init__(self, title, dataset, file_path, storage_total_size, num_top_groups):

        super(UsagePieChart, self).__init__(title=title,
                                            dataset=dataset,
                                            file_path=file_path)

        self.storage_total_size = storage_total_size

        self.num_top_groups = num_top_groups

        self.width = 14

        self.color_name = 'Spectral'

    def _draw(self):

        labels = []
        sizes = []

        self._sort_dataset(lambda group_info: group_info.size, True)

        top_groups_info_list = self.dataset[:self.num_top_groups]

        groups_total_size = \
            UsagePieChart._calc_groups_total_size(self.dataset)

        top_groups_total_size = \
            UsagePieChart._calc_groups_total_size(top_groups_info_list)

        others_size = groups_total_size - top_groups_total_size

        for item in top_groups_info_list:

            label_text = item.name + " (" + nf.number_to_base_2(item.size) + ")"

            labels.append(label_text)
            sizes.append(item.size)

        labels.append("others (" + nf.number_to_base_2(others_size) + ")")
        sizes.append(others_size)

        total_size_pct_used = \
            int((groups_total_size / self.storage_total_size) * Decimal(100))

        sub_title = \
            "Used " + nf.number_to_base_2(groups_total_size) + \
            " of " + nf.number_to_base_2(self.storage_total_size) + \
            " Volume (" + str(total_size_pct_used) + "%)"

        self._ax.set_title(sub_title, fontsize=12, y=1.15)

        self._figure.subplots_adjust(top=0.80)

        color_map = BaseChart._create_colors(self.color_name, len(labels))

        patches, texts, auto_texts = \
            self._ax.pie(sizes, labels=labels,
                         colors=color_map, shadow=False,
                         autopct='%1.2f%%', pctdistance=0.8, startangle=90)

        # Equal aspect ratio ensures that pie is drawn as a circle.
        self._ax.axis('equal')

        for auto_text_item in auto_texts:
            auto_text_item.set_fontsize(10)

    @staticmethod
    def _calc_groups_total_size(group_info_list):

        groups_total_size = 0

        for group_info_item in group_info_list:
            groups_total_size += group_info_item.size

        return groups_total_size
