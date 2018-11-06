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
import datetime

# Force matplotlib to not use any X window backend.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class BaseChart(object):

    def __init__(self, title='', x_label='', y_label='',
                 file_path='', dataset=None):

        __metaclass__ = abc.ABCMeta

        super(BaseChart, self).__init__()

        self.title = title

        self.x_label = x_label
        self.y_label = y_label

        self.file_path = file_path

        self.dataset = list(dataset)

        self._fig = None
        self._file_type = 'svg'

    def create(self):

        self._draw()
        self._save()
        self._close()

    def _sort_dataset(self, key, reverse=False):
        self.dataset.sort(key=key, reverse=reverse)

    def _add_creation_text(self):

        self._fig.text(
            0, 0, datetime.datetime.now().strftime('%Y-%m-%d - %X'),
            verticalalignment='bottom', horizontalalignment='left',
                fontsize=8, transform=self._fig.transFigure)

    def _draw(self):
        raise NotImplementedError("Implement draw method in a sub class!")

    def _save(self):
        plt.savefig(self.file_path, type=self._file_type)

    def _close(self):
        plt.close(self._fig)
        self._fig = None
