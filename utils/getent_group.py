#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2019 Gabriele Iannetti <g.iannetti@gsi.de>
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


def get_user_groups():

    user_groups = list()
    output = subprocess.check_output(['getent', 'group'])
    output_lines = output.strip().split('\n')

    for line in output_lines:

        fields = line.split(':', 3)
        group = fields[0]
        gid = int(fields[2])

        if gid > 999:
            logging.debug("Found User Group %s:%s" % (group, gid))
            user_groups.append(group)
        else:
            logging.debug("Ignoring User Group: %s:%s" % (group, gid))

    return user_groups


