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

from matplotlib import cm
from decimal import Decimal
from lfs import disk_usage_info
from format import number_format
from dataset import dataset_handler

# Force matplotlib to not use any X window backend.
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


# TODO: Remove this. do not remove files from file system. just overwrite.
def cleanup_files(dir_path, pattern):
    if not os.path.isdir(dir_path):
        raise RuntimeError("Directory does not exist under: %s" % dir_path)

    file_list = os.listdir(dir_path)

    for filename in file_list:

        if pattern in filename:
            file_path = os.path.join(dir_path, filename)

            os.remove(file_path)

            logging.debug(
                "Removed file during cleanup procedure: %s" % file_path)


def create_pie_chart(config):

    filesystem = config.get('lustre', 'filesystem')

    chart_report_dir = config.get('base_chart', 'report_dir')
    chart_filetype = config.get('base_chart', 'filetype')
    num_top_groups = config.get('base_chart', 'num_top_groups')

    chart_pie_filename = config.get('pie_chart_disk_used', 'filename')

    logging.debug("Number of top group: %s" % num_top_groups)

    ost_total_size = disk_usage_info.lustre_total_ost_usage(filesystem)

    if not os.path.isdir(chart_report_dir):
        raise RuntimeError(
            "Directory does not exist for saving charts: %s" % chart_report_dir)

    now = datetime.datetime.now()
    snapshot_date = now.strftime('%Y-%m-%d')
    snapshot_timestamp = snapshot_date + " - " + now.strftime('%X')

    cleanup_files(chart_report_dir, chart_pie_filename)

    logging.debug("Report date: %s" % snapshot_date)

    title = "Storage Report of " + filesystem

    # TODO: Must be an attribute of the future class of base chart.
    chart_path = os.path.abspath(chart_report_dir + os.path.sep +
                                 chart_pie_filename + "_" + snapshot_date +
                                 "." + chart_filetype)

    used_total_size = dataset_handler.get_total_size()

    top_group_sizes = dataset_handler.get_top_group_sizes()

    others_size = dataset_handler.calc_others_size(top_group_sizes,
                                                   used_total_size)

    logging.debug("Total size: %s" % used_total_size)
    logging.debug("Other size: %s" % others_size)

    logging.debug("File path for pie chart: %s" % chart_path)

    filetype = os.path.split(chart_path)[1].split('.')[1]

    labels = []
    sizes = []

    for item in top_group_sizes:

        label_text = item.gid + " (" + number_format.number_to_base_2(item.size) + ")"

        labels.append(label_text)
        sizes.append(item.size)

    labels.append("others (" + number_format.number_to_base_2(others_size) + ")")

    sizes.append(others_size)

    creation_timestamp_text = "Timestamp: " + snapshot_timestamp

    fig, ax = plt.subplots()

    fig.suptitle(title, fontsize=18, fontweight='bold')
    fig.subplots_adjust(top=0.80)

    cs_range = float(len(sizes)) * 1.1
    colors = cm.Set1(plt.np.arange(cs_range) / cs_range)

    patches, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                       autopct='%1.2f%%', pctdistance=.8,
                                       shadow=False, startangle=90)

    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.axis('equal')

    for autotext_item in autotexts:
        autotext_item.set_fontsize(10)

    pct_used_total_size = int((used_total_size / ost_total_size) * Decimal(100))

    size_info = "Used " + number_format.number_to_base_2(used_total_size) + \
                " of " + number_format.number_to_base_2(ost_total_size) + \
                " Volume (" + str(pct_used_total_size) + "%)"

    ax.set_title(size_info, y=1.125, fontsize=14)

    ax.text(0, 0, creation_timestamp_text, fontsize=8,
            verticalalignment='bottom', horizontalalignment='left',
            transform=fig.transFigure)

    fig.set_size_inches(10, 8)

    fig.savefig(chart_path, format=filetype, dpi=200)

    logging.debug("Saved created pie chart under: %s" % chart_path)
