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


# Force matplotlib to not use any X window backend.
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import os
import logging
import datetime

from matplotlib import cm
from numbers import Number
from decimal import Decimal

from lfs.disk_usage_info import lustre_ost_disk_usage_info_decimal_base_2
from dataset.dataset_handler import *

PB_DIVISIOR = Decimal(1125899906842624.0)
TB_DIVISIOR = Decimal(1099511627776.0)
GB_DIVISIOR = Decimal(1073741824.0)
MB_DIVISIOR = Decimal(1048576.0)
KB_DIVISIOR = Decimal(1024.0)
B_DIVISIOR = Decimal(1.0)


chart_pie_path = ""


def format_number_to_base_2_byte_unit(number):
    if not isinstance(number, Number):
        raise TypeError("Provided value is not a number: %s" % str(number))

    result = None

    if number >= PB_DIVISIOR:
        result = Decimal(number) / PB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "PiB"

    elif number >= TB_DIVISIOR:
        result = number / TB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "TiB"

    elif number >= GB_DIVISIOR:
        result = number / GB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "GiB"

    elif number >= MB_DIVISIOR:
        result = number / MB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "MiB"

    elif number >= KB_DIVISIOR:
        result = number / KB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "KiB"

    elif number >= B_DIVISIOR:
        result = number / B_DIVISIOR
        result = str(result) + "B"

    else:
        raise ValueError(
            "Failed to format number to a supported byte unit: %s" % str(
                number))

    return result


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

    chart_filetype = config.get('chart', 'filetype')
    chart_report_dir = config.get('chart', 'report_dir')

    num_top_groups = config.get('pie_chart_disk_used', 'num_top_groups')
    chart_pie_filename = config.get('pie_chart_disk_used', 'filename')

    filesystem = config.get('storage', 'filesystem')

    logging.debug("Number of top group: %s" % num_top_groups)

    ost_total_size = lustre_ost_disk_usage_info_decimal_base_2(filesystem)

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
    global chart_pie_path

    chart_pie_path = os.path.abspath(chart_report_dir + os.path.sep + chart_pie_filename + "_" + snapshot_date + "." + chart_filetype)

    used_total_size = get_total_size(config)

    group_info_list = get_top_group_list(config)

    others_size = calc_others_size(group_info_list, used_total_size)

    logging.debug("Total size: %s" % used_total_size)
    logging.debug("Other size: %s" % others_size)

    logging.debug("File path for pie chart: %s" % chart_pie_path)

    filetype = os.path.split(chart_pie_path)[1].split('.')[1]

    labels = []
    sizes = []

    for group_info in group_info_list:
        label_text = group_info.gid + " (" + format_number_to_base_2_byte_unit(
            group_info.size) + ")"

        labels.append(label_text)
        sizes.append(group_info.size)

    labels.append(
        "others (" + format_number_to_base_2_byte_unit(others_size) + ")")
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
    ax.axis(
        'equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    for autotext_item in autotexts:
        autotext_item.set_fontsize(10)

    pct_used_total_size = int((used_total_size / ost_total_size) * Decimal(100))

    size_info = "Used " + format_number_to_base_2_byte_unit(
        used_total_size) + " of " + format_number_to_base_2_byte_unit(
        ost_total_size) + " Volume (" + str(pct_used_total_size) + "%)"

    ax.set_title(size_info, y=1.125, fontsize=14)

    ax.text(0, 0, creation_timestamp_text, fontsize=8,
            verticalalignment='bottom', horizontalalignment='left',
            transform=fig.transFigure)

    fig.set_size_inches(10, 8)

    fig.savefig(chart_pie_path, format=filetype, dpi=200)

    logging.debug("Saved created pie chart under: %s" % chart_pie_path)