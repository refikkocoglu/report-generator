#!/usr/bin/env python
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


import os
import logging
import datetime
import numpy as np
import matplotlib.pyplot as plt

import dataset.dataset_handler as ds
from format import number_format


def draw(group_info_list):

    num_groups = len(group_info_list)

    logging.debug("Number of Groups: %s" % num_groups)

    group_names = list()
    top_bar_list_values = list()
    bottom_bar_list_values = list()

    max_sum_quota_and_disk = 5000
    tick_width_y = max_sum_quota_and_disk / 10

    for group_info in group_info_list:
        logging.debug("%s - %s - %s" % (
            group_info.gid, group_info.size, group_info.quota))

        group_names.append(group_info.gid)

        top_bar_list_values.append(
            int(group_info.quota / number_format.TIB_DIVISIOR))

        bottom_bar_list_values.append(
            int(group_info.size / number_format.TIB_DIVISIOR))

    ind = np.arange(num_groups)  # the x locations for the groups

    bar_width = 0.35  # the width of the bars: can also be len(x) sequence

    fig_width = num_groups
    fig_height = 10.0

    plt.figure(figsize=(fig_width, fig_height))

    p1 = plt.bar(ind, bottom_bar_list_values, bar_width, color='blue')
    p2 = plt.bar(ind, top_bar_list_values, bar_width, color='orange',
                 bottom=bottom_bar_list_values)

    plt.title('Quota and Disk Space Used')
    plt.xlabel('Group')
    plt.ylabel('Disk Space Used (TiB)')

    plt.xticks(ind, group_names)

    plt.yticks(np.arange(0, max_sum_quota_and_disk, tick_width_y))
    plt.legend((p2[0], p1[0]), ('Quota', 'Used'))


def create_stacked_bar(config):

    logging.debug('Creating stacked bar for quota and disk usage per group...')

    chart_report_dir = config.get('base_chart', 'report_dir')
    chart_filetype = config.get('base_chart', 'filetype')

    chart_filename = config.get('stacked_bar_quota_disk_used', 'filename')

    now = datetime.datetime.now()
    snapshot_date = now.strftime('%Y-%m-%d')
    snapshot_timestamp = snapshot_date + " - " + now.strftime('%X')

    # group_info_list = ds.get_group_info_list()
    group_info_list = ds.get_top_group_info_list()

    draw(group_info_list)

    chart_path = os.path.abspath(chart_report_dir + os.path.sep +
                                 chart_filename + "_" + snapshot_date + "." +
                                 chart_filetype)

    plt.savefig(chart_path, format=chart_filetype, dpi=200)

    logging.debug("Saved stacked bar chart under: %s" % chart_path)


def create_stacked_bar_dev():

    group_info_list = create_dummy_group_info_list(20)

    draw(group_info_list)

    plt.savefig('/home/iannetti/tmp/stacked_bar.svg', format='svg', dpi=300)

    plt.show()


def create_dummy_group_info_list(number=None):

    group_info_list = list()

    group_info_list.append(
        ds.GroupInfoItem('asteg', '2612725871277742', '2748779069440000'))
    group_info_list.append(
        ds.GroupInfoItem('alidata', '1984900832193635', '2035196023013376'))
    group_info_list.append(
        ds.GroupInfoItem('hades', '1508392669128129', '1564605046325248'))
    group_info_list.append(
        ds.GroupInfoItem('alice', '1077588550802481', '1319413953331200'))
    group_info_list.append(
        ds.GroupInfoItem('fn', '1022718464634783', '945579999887360'))
    group_info_list.append(
        ds.GroupInfoItem('cbm', '738440430421761', '1209462790553600'))
    group_info_list.append(
        ds.GroupInfoItem('pbar', '375407152760683', '945579999887360'))
    group_info_list.append(
        ds.GroupInfoItem('afseg', '269953044185563', '659706976665600'))
    group_info_list.append(
        ds.GroupInfoItem('land', '114726018555229', '164926744166400'))
    group_info_list.append(
        ds.GroupInfoItem('hyihp', '110467581455500', '142936511610880'))
    group_info_list.append(
        ds.GroupInfoItem('fopi', '106306847077093', '115448720916480'))
    group_info_list.append(
        ds.GroupInfoItem('fltc', '105399288025433', '126443837194240'))
    group_info_list.append(
        ds.GroupInfoItem('ks', '72702387970910', '87960930222080'))
    group_info_list.append(
        ds.GroupInfoItem('tasca', '70261949736621', '71468255805440'))
    group_info_list.append(
        ds.GroupInfoItem('the', '63971130556753', '103354093010944'))
    group_info_list.append(
        ds.GroupInfoItem('ap', '55192157271191', '65970697666560'))
    group_info_list.append(
        ds.GroupInfoItem('had1', '52089033367758', '87960930222080'))
    group_info_list.append(
        ds.GroupInfoItem('bio', '45139228432740', '82463372083200'))
    group_info_list.append(
        ds.GroupInfoItem('alitrain', '39386206628620', '109951162777600'))
    group_info_list.append(
        ds.GroupInfoItem('hij', '29268878252590', '38482906972160'))
    group_info_list.append(
        ds.GroupInfoItem('kc', '17347387740312', '18691697672192'))
    group_info_list.append(
        ds.GroupInfoItem('ukt', '14338270055031', '49478023249920'))
    group_info_list.append(
        ds.GroupInfoItem('uf7', '11561779120430', '76965813944320'))
    group_info_list.append(
        ds.GroupInfoItem('kr', '8886451453013', '17592186044416'))
    group_info_list.append(
        ds.GroupInfoItem('him', '6798995223478', '26388279066624'))
    group_info_list.append(
        ds.GroupInfoItem('rz', '6687087233272', '10995116277760'))
    group_info_list.append(
        ds.GroupInfoItem('tpcdata', '6090686094889', '27487790694400'))
    group_info_list.append(
        ds.GroupInfoItem('kp2', '6086615963545', '6873068560384'))
    group_info_list.append(ds.GroupInfoItem('ufk', '5180489216282', '0'))
    group_info_list.append(
        ds.GroupInfoItem('ul', '5157645070220', '6597069766656'))
    group_info_list.append(
        ds.GroupInfoItem('bhs', '4822637002137', '32985348833280'))
    group_info_list.append(
        ds.GroupInfoItem('hpc', '4555805045551', '25288767438848'))
    group_info_list.append(
        ds.GroupInfoItem('hyphi', '3468981480003', '4509715660800'))
    group_info_list.append(
        ds.GroupInfoItem('kp1', '2833990585812', '2914135310336'))
    group_info_list.append(
        ds.GroupInfoItem('fairgsi', '2440403339127', '5497558138880'))
    group_info_list.append(
        ds.GroupInfoItem('radprot', '2181051911650', '76965813944320'))
    group_info_list.append(ds.GroupInfoItem('root', '790829819336', '0'))
    group_info_list.append(ds.GroupInfoItem('thd', '346240925999', '0'))
    group_info_list.append(ds.GroupInfoItem('rzgast', '133203420737', '0'))
    group_info_list.append(
        ds.GroupInfoItem('hht', '130642827472', '21990232555520'))
    group_info_list.append(ds.GroupInfoItem('ee', '58032178677', '0'))
    group_info_list.append(ds.GroupInfoItem('su', '27676842674', '0'))
    group_info_list.append(
        ds.GroupInfoItem('htit', '16930263228', '42949672960'))
    group_info_list.append(
        ds.GroupInfoItem('psl', '12815424839', '107374182400'))
    group_info_list.append(
        ds.GroupInfoItem('nustar', '5637091577', '107374182400'))
    group_info_list.append(ds.GroupInfoItem('vw', '24472895', '576716800'))
    group_info_list.append(ds.GroupInfoItem('staff', '3846924', '0'))
    group_info_list.append(ds.GroupInfoItem('fat', '2265308', '0'))
    group_info_list.append(ds.GroupInfoItem('997', '939808', '0'))
    group_info_list.append(ds.GroupInfoItem('99', '764464', '0'))
    group_info_list.append(ds.GroupInfoItem('81', '636848', '0'))
    group_info_list.append(ds.GroupInfoItem('156', '441904', '0'))
    group_info_list.append(
        ds.GroupInfoItem('astrum', '125315', '1099511627776'))
    group_info_list.append(ds.GroupInfoItem('tty', '39072', '0'))
    group_info_list.append(ds.GroupInfoItem('rzg-int', '23638', '0'))
    group_info_list.append(ds.GroupInfoItem('utmp', '22384', '0'))
    group_info_list.append(ds.GroupInfoItem('systemd-bus-proxy', '17346', '0'))
    group_info_list.append(ds.GroupInfoItem('120', '12288', '0'))
    group_info_list.append(ds.GroupInfoItem('man', '8192', '0'))
    group_info_list.append(ds.GroupInfoItem('mail', '8192', '0'))
    group_info_list.append(ds.GroupInfoItem('35', '8192', '0'))
    group_info_list.append(ds.GroupInfoItem('bel', '4096', '10995116277760'))
    group_info_list.append(ds.GroupInfoItem('adm', '1192', '0'))
    group_info_list.append(ds.GroupInfoItem('fsr', '0', '576716800'))

    if number:
        return group_info_list[:number]
    else:
        return group_info_list


create_stacked_bar_dev()

