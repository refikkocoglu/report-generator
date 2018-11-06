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

from chart.quota_pct_bar_chart import QuotaPctBarChart
from chart.usage_quota_bar_chart import UsageQuotaBarChart
from chart.usage_pie_chart import UsagePieChart


def create_usage_pie_chart(group_info_list, file_path):

    chart = UsagePieChart(title='Storage Report of fs',
                          file_path=file_path,
                          dataset=group_info_list,
                          storage_total_size=18458963071860736)

    chart.create()


def create_quota_pct_bar_chart(group_info_list, file_path):

    chart = QuotaPctBarChart(title='Group Quota Usage of fs',
                             sub_title='Procedural Usage per Group',
                             file_path=file_path,
                             dataset=group_info_list)

    chart.create()


def create_usage_quota_bar_chart(group_info_list, file_path):
    
    chart = UsageQuotaBarChart(
        title="Group Disk and Quota Usage of fs",
        file_path=file_path,
        dataset=group_info_list)

    chart.create()


def main():

    logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s: %(message)s')

    logging.debug("START")

    group_info_list = ds.create_dummy_group_info_list()

    create_usage_pie_chart(
        group_info_list,
        '/home/iannetti/tmp/fs_usage_pie_YYYY-WW.svg'
    )

    create_quota_pct_bar_chart(
        group_info_list,
        '/home/iannetti/tmp/fs_soft_quota_pcnt_YYYY-WW.svg'
    )

    create_usage_quota_bar_chart(
        group_info_list,
        '/home/iannetti/tmp/fs_usage+quota_bar_YYYY-WW.svg'
    )

    logging.debug("END")


if __name__ == '__main__':
   main()
