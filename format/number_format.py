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


from numbers import Number
from decimal import Decimal


PIB_DIVISIOR = Decimal(1125899906842624.0)
TIB_DIVISIOR = Decimal(1099511627776.0)
GIB_DIVISIOR = Decimal(1073741824.0)
MIB_DIVISIOR = Decimal(1048576.0)
KIB_DIVISIOR = Decimal(1024.0)
B_DIVISIOR = Decimal(1.0)


def number_to_base_2(number):
    
    if not isinstance(number, Number):
        raise TypeError("Provided value is not a number: %s" % str(number))

    result = None

    if number >= PIB_DIVISIOR:
        result = Decimal(number) / PIB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "PiB"

    elif number >= TIB_DIVISIOR:
        result = Decimal(number) / TIB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "TiB"

    elif number >= GIB_DIVISIOR:
        result = Decimal(number) / GIB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "GiB"

    elif number >= MIB_DIVISIOR:
        result = Decimal(number) / MIB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "MiB"

    elif number >= KIB_DIVISIOR:
        result = Decimal(number) / KIB_DIVISIOR
        result = round(result, 2)
        result = str(result) + "KiB"

    elif number >= B_DIVISIOR:
        result = Decimal(number) / B_DIVISIOR
        result = str(result) + "B"

    else:
        raise ValueError(
            "Failed to format number to a supported byte unit: %s" % str(
                number))

    return result