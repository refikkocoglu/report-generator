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


import abc
import sys
import datetime

# Force matplotlib to not use any X window backend.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class BaseChart(object):

    def __init__(self, title, dataset, file_path,
                 sub_title='', width=20, height=10, x_label='', y_label=''):

        __metaclass__ = abc.ABCMeta

        super(BaseChart, self).__init__()

        self.title = title
        self.dataset = dataset
        self.file_path = file_path

        self.sub_title = sub_title

        self.width = width
        self.height = height

        self.x_label = x_label
        self.y_label = y_label

        self._file_type = 'svg'

        self._figure = None
        self._ax = None

    def create(self):

        self._figure, self._ax = plt.subplots(figsize=(self.width, self.height))

        self._draw()

        self._set_figure_and_axis_attr()
        self._add_creation_text()

        self._save()
        self._close()

    # TODO: Extract that method to proper item class maybe it returns a copy then...
    def _sort_dataset(self, key, reverse=False):

        if isinstance(self.dataset, list):
            self.dataset.sort(key=key, reverse=reverse)

    def _add_creation_text(self):

        self._figure.text(
            0, 0, datetime.datetime.now().strftime('%Y-%m-%d - %X'),
            verticalalignment='bottom', horizontalalignment='left',
                fontsize=8, transform=self._figure.transFigure)

    def _set_figure_and_axis_attr(self):

        self._figure.suptitle(self.title, fontsize=18, fontweight='bold')

        self._ax.set_title(self.sub_title, fontsize=12, y=1.15)

        self._ax.set_xlabel(self.x_label)
        self._ax.set_ylabel(self.y_label)

    @abc.abstractmethod
    def _draw(self):
        raise NotImplementedError(
            "Not implemented method: %s.%s" %
            (self.__class__, sys._getframe().f_code.co_name))

    def _save(self):
        plt.savefig(self.file_path, type=self._file_type)

    def _close(self):
        plt.close(self._figure)
