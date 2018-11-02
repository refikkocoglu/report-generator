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

    def __init__(self, title='', sub_title='', file_path='', dataset=None):

        x_label = 'Group'
        y_label = 'Quota Usage (%)'

        super(DiskUsageChart, self).__init__(title, x_label, y_label,
                                             file_path, dataset)

        self.sub_title = "Procedural Usage per Group"

        self.top_group_sizes = 0
        self.others_size = 0
        self.groups_total_size = 0
        self.ost_total_size = 0
        self.snapshot_timestamp = ""

    def _draw(self):

        labels = []
        sizes = []

        for item in self.dataset:
            label_text = item.name + " (" + nf.number_to_base_2(item.size) + ")"

            labels.append(label_text)
            sizes.append(item.size)

        labels.append("others (" + nf.number_to_base_2(self.others_size) + ")")

        sizes.append(self.others_size)

        creation_timestamp_text = "Timestamp: " + self.snapshot_timestamp

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

        pct_used_total_size = int((self.groups_total_size / self.ost_total_size) * Decimal(100))

        size_info = "Used " + nf.number_to_base_2(self.groups_total_size) + \
                    " of " + nf.number_to_base_2(self.ost_total_size) + \
                    " Volume (" + str(pct_used_total_size) + "%)"

        ax.set_title(size_info, y=1.125, fontsize=14)

        ax.text(0, 0, creation_timestamp_text, fontsize=8,
                verticalalignment='bottom', horizontalalignment='left',
                transform=self._fig.transFigure)

        self._fig.set_size_inches(10, 8)


def create_pie_chart(config):

    filesystem = config.get('lustre', 'filesystem')

    chart_report_dir = config.get('base_chart', 'reports_dir')
    chart_filetype = config.get('base_chart', 'file_type')
    num_top_groups = config.get('base_chart', 'num_top_groups')

    chart_pie_filename = config.get('pie_chart_disk_used', 'filename')

    ost_total_size = disk_usage_info.lustre_total_ost_usage(filesystem)

    if not os.path.isdir(chart_report_dir):
        raise RuntimeError(
            "Directory does not exist for saving charts: %s" % chart_report_dir)

    now = datetime.datetime.now()
    snapshot_date = now.strftime('%Y-%m-%d')
    snapshot_timestamp = snapshot_date + " - " + now.strftime('%X')

    title = "Storage Report of " + filesystem

    # TODO: Must be an attribute of the future class of base chart.
    chart_path = os.path.abspath(chart_report_dir + os.path.sep +
                                 chart_pie_filename + "_" + snapshot_date +
                                 "." + chart_filetype)

    groups_total_size = ds.get_groups_total_size()

    top_group_sizes = ds.get_top_group_sizes()

    others_size = ds.calc_others_size(top_group_sizes, groups_total_size)

    file_type = os.path.split(chart_path)[1].split('.')[1]

    fig = draw(top_group_sizes, others_size, snapshot_timestamp, title,
               groups_total_size, ost_total_size)

    fig.savefig(chart_path, format=file_type, dpi=300)
