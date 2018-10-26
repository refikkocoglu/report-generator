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


import os
import logging
import datetime
import numpy as np
import matplotlib.pyplot as plt

import dataset.dataset_handler as ds
from format import number_format


def draw(group_info_list):

    num_groups = len(group_info_list)

    logging.debug("Number of Groups: %s" % num_groups)

    group_names = list()
    top_bar_list_values = list()
    bottom_bar_list_values = list()

    max_sum_quota_and_disk = float(
        (group_info_list[0].size + group_info_list[0].quota)
        / number_format.TIB_DIVISIOR)

    tick_width_y = 200

    for group_info in group_info_list:
        logging.debug("%s - %s - %s" % (
            group_info.gid, group_info.size, group_info.quota))

        group_names.append(group_info.gid)

        top_bar_list_values.append(
            int(group_info.quota / number_format.TIB_DIVISIOR))

        bottom_bar_list_values.append(
            int(group_info.size / number_format.TIB_DIVISIOR))

    ind = np.arange(num_groups)  # the x locations for the groups

    bar_width = 0.35  # the width of the bars: can also be len(x) sequence

    fig_width = num_groups
    fig_height = 10.0

    plt.figure(figsize=(fig_width, fig_height))

    p1 = plt.bar(ind, bottom_bar_list_values, bar_width, color='blue')
    p2 = plt.bar(ind, top_bar_list_values, bar_width, color='orange',
                 bottom=bottom_bar_list_values)

    plt.title('Quota and Disk Space Used')
    plt.xlabel('Group')
    plt.ylabel('Disk Space Used (TiB)')

    plt.xticks(ind, group_names)

    plt.yticks(np.arange(0, max_sum_quota_and_disk, tick_width_y))
    plt.legend((p2[0], p1[0]), ('Quota', 'Used'))


def create_stacked_bar(config):

    logging.debug('Creating stacked bar for quota and disk usage per group...')

    chart_report_dir = config.get('base_chart', 'report_dir')
    chart_filetype = config.get('base_chart', 'filetype')

    chart_filename = config.get('stacked_bar_quota_disk_used', 'filename')

    now = datetime.datetime.now()
    snapshot_date = now.strftime('%Y-%m-%d')
    snapshot_timestamp = snapshot_date + " - " + now.strftime('%X')

    # group_info_list = ds.get_group_info_list()
    group_info_list = ds.get_top_group_info_list()

    draw(group_info_list)

    chart_path = os.path.abspath(chart_report_dir + os.path.sep +
                                 chart_filename + "_" + snapshot_date + "." +
                                 chart_filetype)

    plt.savefig(chart_path, format=chart_filetype, dpi=300)

    logging.debug("Saved stacked bar chart under: %s" % chart_path)


def create_stacked_bar_dev(file_path, num_groups=None):

    group_info_list = ds.create_dummy_group_info_list(num_groups)

    draw(group_info_list)

    plt.savefig(file_path, format='svg', dpi=300)

    plt.show()
