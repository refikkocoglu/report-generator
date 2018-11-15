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


import pandas as pd

# Force matplotlib to not use any X window backend.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from base_chart import BaseChart


class UsageTrendChart(BaseChart):

    def __init__(self, title, dataset, file_path, start_date, end_date):

        super(UsageTrendChart, self).__init__(title, dataset, file_path)

        self._start_date = start_date
        self._end_date = end_date

    def _draw(self):

        date_interval = \
            pd.date_range(self._start_date, self._end_date, freq='D')

        data_frame = pd.DataFrame(index=date_interval)

        #TODO: Data structure in dataset???
        for group_name in self.dataset:

            dates = pd.DatetimeIndex(
                self.dataset[group_name][0], dtype='datetime64')

            data_frame[group_name] = \
                pd.Series(self.dataset[group_name][1], index=dates)

        mean_weekly_summary = data_frame.resample('W').mean()

        mean_weekly_summary = \
            mean_weekly_summary.truncate(
                before=self._start_date, after=self._end_date)

        print(mean_weekly_summary)

        mean_weekly_summary.plot(ax=self._ax)

        self._ax.legend(title="Groups", fontsize='xx-small', loc='upper left')
