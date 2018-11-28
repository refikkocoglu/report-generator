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


def create_data_frame(item_dict):

    data_frame = pd.DataFrame()

    for group_name in item_dict:

        dates = pd.DatetimeIndex(item_dict[group_name][0], dtype='datetime64')

        data_frame[group_name] = pd.Series(item_dict[group_name][1], index=dates)

    start_date = data_frame.index.min().strftime('%Y-%m-%d')
    end_date = data_frame.index.max().strftime('%Y-%m-%d')

    mean_weekly_summary = data_frame.resample('W').mean()

    return mean_weekly_summary.truncate(before=start_date, after=end_date)