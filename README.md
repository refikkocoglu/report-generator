# Storage Report Generator

## Prerequisite

**Required**:  
* python36 - Python runtime
* matplotlib (3.1.1) - for plotting
* pandas (0.25.1) - for time series plots

**Optional**:  
* pip3 - installation of Python packages
* mysqlclient (1.4.4) - collecting and retrieving data from MySQL-DB
* getent - group resolution
* lfs quota - determining Lustre FS group quotas

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

## Dependency Matrix

**TODO** - which component depends on what module

## Report Examples

**TODO** - add local created reports for showing examples
