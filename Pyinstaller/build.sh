#!/bin/bash
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


TARGET_DIR=pybuild
SOURCE_DIR=../../

# Use pyinstaller default paths:
# --distpath=.dist
# --workpath=.build

LUSTRE_GROUP_QUOTA_COLLECT_EXE=lustre-group-quota-collect.py
LUSTRE_WEEKLY_REPORTS_EXE=lustre-weekly-reports.py
LUSTRE_MONTHLY_REPORTS_EXE=lustre-monthly-reports.py
LUSTRE_MIGRATION_REPORT_EXE=lustre-migration-report.py


# $1 = expects executable file
function build() {

    if [ "$#" -ne 1 ]; then
        echo "Build function expects executable file!"
        exit 2
    fi

    EXE=$1

    mkdir -p "$TARGET_DIR"
    cd "$TARGET_DIR"

    $(pyinstaller --onefile --name ${EXE} $SOURCE_DIR/${EXE})

    if [ -f "dist/${EXE}" ]; then
        echo ""
        echo ">>> SUCCESSFUL BUILD: dist/${EXE}"
    else
        echo ""
        echo ">>> FAILED BUILD: dist/${EXE}"
    fi

    cd - 1>/dev/null

}

case "$1" in

    all)

        build ${LUSTRE_GROUP_QUOTA_COLLECT_EXE}
        build ${LUSTRE_WEEKLY_REPORTS_EXE}
        build ${LUSTRE_MONTHLY_REPORTS_EXE}
        build ${LUSTRE_MIGRATION_REPORT_EXE}
    ;;

    quota-collect)
        build ${LUSTRE_GROUP_QUOTA_COLLECT_EXE}
    ;;

    weekly-reports)
        build ${LUSTRE_WEEKLY_REPORTS_EXE}
    ;;

    monthly-reports)
        build ${LUSTRE_MONTHLY_REPORTS_EXE}
    ;;

    migration-report)
        build ${LUSTRE_MIGRATION_REPORT_EXE}
    ;;

    clean)
        $(rm -r "$TARGET_DIR")
    ;;

    *)
        echo "Usage: $0 {all|quota-collect|weekly-reports|monthly-reports|migration-report|clean}"
        exit 1
    ;;

esac
