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

# Force matplotlib to not use any X window backend.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class BaseChart(object):

    def __init__(self):

        __metaclass__ = abc.ABCMeta

        super(BaseChart, self).__init__()

        self.title = ""
        self.sub_title = ""

        self.x_label = ""
        self.y_label = ""

        self.file_type = 'svg'

    def draw(self, groups_list):
        raise NotImplementedError("Implement draw method in a sub class!")

    def save(self, file_path):

        # TODO: understand plt works, multiple calls???
        # What happens without a savefig with plt object?
        # Could plt being messed up with inconsistency?
        plt.savefig(file_path, type=self.file_type)
