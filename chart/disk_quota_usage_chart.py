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
import logging
import datetime
import numpy as np
from format import number_format

# Force matplotlib to not use any X window backend.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class DiskQuotaUsageChart(BaseChart):

    def __init__(self):

        super(DiskQuotaUsageChart, self).__init__()

        self.title = "Group Disk and Quota Usage of Lustre Nyx"
        self.sub_title = "Whatever"

        self.x_label = 'Group'
        self.y_label = 'Disk Space Used (TiB)'

    def draw(self, group_info_list):

        num_groups = len(group_info_list)

        logging.debug("Number of Groups: %s" % num_groups)

        group_names = list()
        quota_list_values = list()
        size_list_values = list()

        tick_width_y = 200

        max_y = float(group_info_list[0].quota /
                      number_format.TIB_DIVISIOR) + tick_width_y

        for group_info in group_info_list:
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

        plt.figure(figsize=(fig_width, fig_height))

        p1 = plt.bar(ind, size_list_values, bar_width, color='blue')
        p2 = plt.bar(ind + bar_width, quota_list_values, bar_width, color='orange')

        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)

        plt.xticks(ind + bar_width / 2, group_names)

        plt.yticks(np.arange(0, max_y, tick_width_y))
        plt.legend((p2[0], p1[0]), ('Quota', 'Used'))


def create_multiple_x_bar(config, group_info_list):

    logging.debug('Creating multi-x bar for quota and disk usage per group...')

    chart_report_dir = config.get('base_chart', 'reports_dir')
    chart_filetype = config.get('base_chart', 'file_type')

    chart_filename = config.get('stacked_bar_quota_disk_used', 'filename')

    now = datetime.datetime.now()
    snapshot_date = now.strftime('%Y-%m-%d')
    snapshot_timestamp = snapshot_date + " - " + now.strftime('%X')

    sorted_group_info_list = sorted(group_info_list,
                                    key=lambda group_info: group_info.quota,
                                    reverse=True)

    draw(sorted_group_info_list)

    chart_path = os.path.abspath(chart_report_dir + os.path.sep +
                                 chart_filename + "_" + snapshot_date + "." +
                                 chart_filetype)

    plt.savefig(chart_path, format=chart_filetype, dpi=300)

    logging.debug("Saved stacked bar chart under: %s" % chart_path)
