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

from chart import multiple_x_bar
from chart import bar_chart
from chart import pie_chart


def main():

    logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s: %(message)s')

    logging.debug("START")

    multiple_x_bar.create_multiple_x_bar_dev(
        '/home/iannetti/tmp/quota_and_disk_usage_report.svg', 20
    )

    bar_chart.create_bar_chart_dev(
        '/home/iannetti/tmp/quota_pct_usage_report.svg', 20
    )

    pie_chart.create_pie_chart_dev(
        '/home/iannetti/tmp/disk_space_usage_report.svg'
    )

    logging.debug("END")


if __name__ == '__main__':
   main()
