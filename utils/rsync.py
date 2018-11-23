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
import subprocess
import os


def transfer_report(run_mode, time_point, path, config):

    if not path:
        raise RuntimeError('Empty path for report found!')

    remote_host = config.get('transfer', 'host')
    remote_path = config.get('transfer', 'path')
    service_name = config.get('transfer', 'service')

    remote_target = \
        remote_host + "::" + remote_path + "/" + time_point.strftime('%Y') + "/"

    if run_mode == 'weekly':
        remote_target += run_mode + "/" + time_point.strftime('%V') + "/"
    elif run_mode == 'monthly':
        remote_target += run_mode + "/" + time_point.strftime('%m') + "/"
    else:
        raise RuntimeError('Undefined run_mode detected: %s' % run_mode)

    remote_target += service_name + "/"

    if not os.path.isfile(path):
        raise RuntimeError('File was not found: %s' % path)

    try:

        subprocess.check_output(["rsync", path, remote_target])

        logging.debug('rsync %s - %s' % (path, remote_target))

    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.output)
