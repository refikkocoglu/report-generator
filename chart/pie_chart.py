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
import datetime
import format.number_format as nf
import dataset.dataset_handler as ds

from matplotlib import cm
from decimal import Decimal
from lfs import disk_usage_info

# Force matplotlib to not use any X window backend.
# import matplotlib as mpl
# mpl.use('Agg')

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


def draw(top_group_sizes, others_size, snapshot_timestamp, title,
         groups_total_size, ost_total_size):

    labels = []
    sizes = []

    for item in top_group_sizes:
        label_text = item.gid + " (" + nf.number_to_base_2(item.size) + ")"

        labels.append(label_text)
        sizes.append(item.size)

    labels.append("others (" + nf.number_to_base_2(others_size) + ")")

    sizes.append(others_size)

    creation_timestamp_text = "Timestamp: " + snapshot_timestamp

    fig, ax = plt.subplots()

    fig.suptitle(title, fontsize=18, fontweight='bold')
    fig.subplots_adjust(top=0.80)

    patches, texts, auto_texts = \
        ax.pie(sizes, labels=labels, autopct='%1.2f%%', pctdistance=0.8,
               shadow=False, startangle=90)

    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.axis('equal')

    for auto_text_item in auto_texts:
        auto_text_item.set_fontsize(10)

    pct_used_total_size = int((groups_total_size / ost_total_size) * Decimal(100))

    size_info = "Used " + nf.number_to_base_2(groups_total_size) + \
                " of " + nf.number_to_base_2(ost_total_size) + \
                " Volume (" + str(pct_used_total_size) + "%)"

    ax.set_title(size_info, y=1.125, fontsize=14)

    ax.text(0, 0, creation_timestamp_text, fontsize=8,
            verticalalignment='bottom', horizontalalignment='left',
            transform=fig.transFigure)

    fig.set_size_inches(10, 8)

    return fig


def create_pie_chart(config):

    filesystem = config.get('lustre', 'filesystem')

    chart_report_dir = config.get('base_chart', 'report_dir')
    chart_filetype = config.get('base_chart', 'filetype')
    num_top_groups = config.get('base_chart', 'num_top_groups')

    chart_pie_filename = config.get('pie_chart_disk_used', 'filename')

    ost_total_size = disk_usage_info.lustre_total_ost_usage(filesystem)

    if not os.path.isdir(chart_report_dir):
        raise RuntimeError(
            "Directory does not exist for saving charts: %s" % chart_report_dir)

    now = datetime.datetime.now()
    snapshot_date = now.strftime('%Y-%m-%d')
    snapshot_timestamp = snapshot_date + " - " + now.strftime('%X')

    cleanup_files(chart_report_dir, chart_pie_filename)

    title = "Storage Report of " + filesystem

    # TODO: Must be an attribute of the future class of base chart.
    chart_path = os.path.abspath(chart_report_dir + os.path.sep +
                                 chart_pie_filename + "_" + snapshot_date +
                                 "." + chart_filetype)

    groups_total_size = ds.get_groups_total_size()

    top_group_sizes = ds.get_top_group_sizes()

    others_size = ds.calc_others_size(top_group_sizes, groups_total_size)

    filetype = os.path.split(chart_path)[1].split('.')[1]

    fig = draw(top_group_sizes, others_size, snapshot_timestamp, title,
               groups_total_size, ost_total_size)

    fig.savefig(chart_path, format=filetype, dpi=300)


def create_pie_chart_dev(file_path):

    title = 'Disk Usage Report'

    num_top_groups = 8

    groups_info_list = ds.create_dummy_group_info_list()

    groups_total_size = 0

    # TODO: Refactor, get group total size...
    for group_size_item in groups_info_list:
        groups_total_size += group_size_item.size

    top_group_info_list = groups_info_list[:num_top_groups]

    top_group_total_size = 0

    # TODO: Refactor, get group total size...
    for group_size_item in top_group_info_list:
        top_group_total_size += group_size_item.size

    # TODO: Why passing list instead of size itself?
    others_size = ds.calc_others_size(top_group_info_list, groups_total_size)

    ost_total_size = 18458963071860736

    snapshot_timestamp = '2018-10-10 00:00:00'

    fig = draw(top_group_info_list, others_size, snapshot_timestamp, title,
         groups_total_size, ost_total_size)

    fig.savefig(file_path, format='svg', dpi=300)

    fig.show()
