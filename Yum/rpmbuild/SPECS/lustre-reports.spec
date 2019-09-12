Name:       lustre-reports
Version:    0.4.1
Release:    1
Summary:    Report Generator for Lustre FS
License:    GPLv3
URL:        https://git.gsi.de/hpc/data/report-generator/

%description
Report Generator for Lustre FS

Consists of the following programs:
* lustre-group-quota-collect.py
* lustre-migration-report.py
* lustre-monthly-reports.py
* lustre-weekly-reports.py

%prep
# no prep

%build
# no build

%install

mkdir -p %{buildroot}/%{_sbindir}

install -m 755 %{__distdir}/lustre-group-quota-collect.py %{buildroot}/%{_sbindir}/lustre-group-quota-collect.py
install -m 755 %{__distdir}/lustre-migration-report.py %{buildroot}/%{_sbindir}/lustre-migration-report.py
install -m 755 %{__distdir}/lustre-monthly-reports.py %{buildroot}/%{_sbindir}/lustre-monthly-reports.py
install -m 755 %{__distdir}/lustre-weekly-reports.py %{buildroot}/%{_sbindir}/lustre-weekly-reports.py

%clean
rm -rf %{buildroot}

%files
/usr/sbin/lustre-group-quota-collect.py
/usr/sbin/lustre-migration-report.py
/usr/sbin/lustre-monthly-reports.py
/usr/sbin/lustre-weekly-reports.py

%changelog
* 0.1             Stable version with weekly created reports.
* 0.2             Trend Charts included.
* 0.2.1           Updated executables and config files.
* 0.2.2           Trend Chart with prev_months number.
* 0.3             Use 'lfs'-based data source.
* 0.4             Migration to Python36
* 0.4.1           Configuration refactored with transfer mode option
