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


import re
import os
import logging
import subprocess

from item_handler import GroupInfoItem

from decimal import Decimal


LFS_BIN = '/usr/bin/lfs'


def check_lfs_binary():

    if not os.path.isfile(LFS_BIN):
        raise RuntimeError("LFS binary was not found under: '%s'" % LFS_BIN)


def lustre_total_size(path):

    total_size_ost = Decimal(0)

    output = subprocess.check_output(["lfs", "df", path])

    if output:

        lines = output.splitlines()

        # TODO Check first line: UUID                   1K-blocks        Used   Available Use% Mounted on

        for line in lines:

            if 'OST' in line:

                fields = line.split()

                ost_size = Decimal(fields[1]) * Decimal(1024.0)

                total_size_ost += ost_size

            else:
                logging.debug("Ignoring 'lfs df' line: %s" % line)

    if total_size_ost:
        return total_size_ost
    else:
        raise RuntimeError("Total OST size of '%s' is 0!" % path)


def create_group_info_item(gid, fs):

    # Example output of 'lfs quota' for group 'rz':
    #
    ## Disk quotas for grp rz (gid 1002):      
    ## Filesystem  kbytes   quota   limit   grace   files   quota   limit   grace
    ## /lustre/hebe 8183208892  107374182400 161061273600       - 2191882       0       0       -  
    
    output = subprocess.check_output(['sudo', LFS_BIN, 'quota', '-g', gid, fs])
   
    lines = output.rstrip().split('\n')

    if len(lines) != 3:
        raise RuntimeError("'lfs quota' output did not return not 3 lines: %s" 
            % output)

    fields_line = lines[2].strip()
    
    # Replace multiple whitespaces with one to split the fields on whitespace.
    fields = re.sub(r'\s+', ' ', fields_line).split(' ')

    kbytes_field = fields[1]
    kbytes_used = None
   
    # exclude '*' in kbytes field, if quota is exceeded!
    if kbytes_field[-1] == '*':
        kbytes_used = int(kbytes_field[:-1])
    else:
        kbytes_used = int(kbytes_field)

    bytes_used = kbytes_used * 1024

    kbytes_quota = int(fields[2])
    bytes_quota = kbytes_quota * 1024

    return GroupInfoItem(gid, bytes_used, bytes_quota)


# TODO: Check group not exists...

def retrieve_group_quota(gid, fs):

    output = subprocess.check_output(['sudo', LFS_BIN, 'quota', '-g', gid, fs])
    
    return _extract_soft_quota(output)


def retrieve_user_quota(uid, fs):

    output = subprocess.check_output(['sudo', LFS_BIN, 'quota', '-u', uid, fs])

    return _extract_soft_quota(output)


def _extract_soft_quota(output):

    lines = output.rstrip().split('\n')

    if len(lines) != 3:
        raise RuntimeError("Output has more than 3 lines: %s" % output)

    fields_line = lines[2].strip()
    
    # Replace multiple whitespaces with one to split the fields on whitespace.
    fields = re.sub(r'\s+', ' ', fields_line).split(' ')

    kbytes_quota = int(fields[2])
    bytes_quota = kbytes_quota * 1024
    
    return bytes_quota
