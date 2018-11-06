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


def create_disk_usage_chart(group_info_list, file_path):

    title = 'Disk Usage Report'

    chart = DiskUsageChart(title=title,
                           file_path=file_path,
                           dataset=group_info_list,
                           storage_total_size=18458963071860736)

    chart.create()


def create_quota_usage_chart(group_info_list, file_path):

    chart = QuotaUsageChart(title="Group Quota Usage of Lustre Nyx",
                            file_path=file_path,
                            dataset=group_info_list)

    chart.create()


def create_disk_quota_usage_chart(group_info_list, file_path):
    
    chart = DiskQuotaUsageChart(
        title="Group Disk and Quota Usage of Lustre Nyx",
        file_path=file_path,
        dataset=group_info_list)

    chart.create()


def main():

    logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s: %(message)s')

    logging.debug("START")

    group_info_list = ds.create_dummy_group_info_list()

    create_disk_usage_chart(
        group_info_list,
        '/home/iannetti/tmp/disk_usage_report.svg'
    )

    create_quota_usage_chart(
        group_info_list,
        '/home/iannetti/tmp/quota_usage_report.svg'
    )

    create_disk_quota_usage_chart(
        group_info_list,
        '/home/iannetti/tmp/disk_quota_usage_report.svg'
    )

    logging.debug("END")


if __name__ == '__main__':
   main()
