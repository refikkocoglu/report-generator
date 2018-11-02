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


import logging
import dataset.dataset_handler as ds

from chart.quota_usage_chart import QuotaUsageChart
from chart.disk_quota_usage_chart import DiskQuotaUsageChart
from chart.disk_usage_chart import DiskUsageChart


def create_disk_usage_chart(file_path, num_top_groups = 8):

    title = 'Disk Usage Report'

    groups_info_list = ds.create_dummy_group_info_list()

    groups_total_size = 0

    for group_size_item in groups_info_list:
        groups_total_size += group_size_item.size

    # TODO: Sort by size in list first and slice the num_top_groups.

    top_group_info_list = groups_info_list[:num_top_groups]

    top_group_total_size = 0

    for group_size_item in top_group_info_list:
        top_group_total_size += group_size_item.size

    # TODO: Why passing list instead of size itself?
    others_size = ds.calc_others_size(top_group_info_list, groups_total_size)

    chart = DiskUsageChart(title=title,
                           file_path=file_path,
                           dataset=top_group_info_list)

    chart.top_group_sizes = top_group_total_size
    chart.others_size = others_size
    chart.groups_total_size = groups_total_size
    chart.ost_total_size = 18458963071860736
    chart.snapshot_timestamp = '2018-10-10 00:00:00'

    chart.create()


def create_quota_usage_chart(file_path, num_groups=10):

    group_info_list = ds.create_dummy_group_info_list(num_groups)

    chart = QuotaUsageChart(title="Group Quota Usage of Lustre Nyx",
                            file_path=file_path,
                            dataset=group_info_list)

    chart.create()


def create_disk_quota_usage_chart(file_path, num_groups=10):

    group_info_list = ds.create_dummy_group_info_list(num_groups)

    chart = DiskQuotaUsageChart(
        title="Group Disk and Quota Usage of Lustre Nyx",
        file_path=file_path,
        dataset=group_info_list)

    chart.create()


def main():

    logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s: %(message)s')

    logging.debug("START")

    create_disk_usage_chart(
        '/home/iannetti/tmp/disk_usage_report.svg'
    )

    create_quota_usage_chart(
        '/home/iannetti/tmp/quota_usage_report.svg'
    )

    create_disk_quota_usage_chart(
        '/home/iannetti/tmp/disk_quota_usage_report.svg'
    )

    logging.debug("END")


if __name__ == '__main__':
   main()
