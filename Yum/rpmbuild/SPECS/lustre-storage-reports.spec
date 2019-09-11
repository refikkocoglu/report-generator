Name:       lustre-storage-reports
Version:    0.4
Release:    0
Summary:    Lustre Storage Reports Generator Scripts at HPC-GSI
License:    GPLv3
URL:        https://git.gsi.de/hpc/data/storage-report-generator/

%description
Lustre Storage Reports Generator

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
# TODO
