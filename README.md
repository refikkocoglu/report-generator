# Storage Report Generator

## Prerequisite

### Python

* Python36
* pip3 
* mysqlclient (1.4.4)
* matplotlib (3.1.1)
* pandas (0.25.1)

### External Binaries

* getent
* lfs quota

### Build Tools Dependencies

__Python__:  

* python36-devel

__mysqlclient:__  

* gcc
* MariaDB-devel
* MariaDB-shared

## Executables

### Lustre Specific

#### Collect Scripts

* lustre-group-quota-collect.py

#### Report Scripts

* lustre-weekly-reports.py
* lustre-monthly-reports.py
* lustre-migration-report.py
