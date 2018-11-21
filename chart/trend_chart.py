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


class TrendChart(BaseChart):

    def __init__(self, title, dataset, file_path,
                 x_label, y_label, start_date, end_date):

        sub_title = "Date from %s to %s" % (start_date, end_date)

        super(TrendChart, self).__init__(title, dataset, file_path, sub_title,
                                         x_label, y_label)

        self._start_date = start_date
        self._end_date = end_date

        # No bright colors.
        self.color_name = 'Dark2'

    def _add_legend(self):

        import operator

        handles, labels = self._ax.get_legend_handles_labels()

        hl = sorted(zip(handles, labels), key=operator.itemgetter(1))

        sorted_handles, sorted_labels = zip(*hl)

        self._figure.legend(handles=sorted_handles, labels=sorted_labels,
                            title="Groups", fontsize='small', loc='upper left',
                            handlelength=3)

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

        line_style_def = ['-', '--', '-.', ':']
        len_lsd = len(line_style_def)
        line_styles = list()

        for i in range(len(self.dataset.keys())):
            line_styles.append(line_style_def[i % len_lsd])

        self._ax.yaxis.set_major_locator(plt.MaxNLocator(12))

        color_map = \
            BaseChart._create_colors(self.color_name, len(self.dataset.keys()))

        mean_weekly_summary.plot(ax=self._ax, legend=False, style=line_styles,
                                 color=color_map, grid=True)

        self._ax.set_title(self.sub_title, fontsize=12)

        self._add_legend()
