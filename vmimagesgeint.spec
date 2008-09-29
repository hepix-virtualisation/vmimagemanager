Summary: vmimagesgeint
Name: vmimagesgeint
Version: 0.0.5
Vendor: LCG/CERN
Release: 0
License: LCG
Group: LCG
Source: %{name}.src.tgz
BuildArch: noarch
Prefix:	/opt/vmimagesgeint
BuildRoot: %{_tmppath}/%{name}-%{version}-build
Packager: support-lcg-manual-install@cern.ch


#requires: java-1.5.0-sun

%description
Integration scripts between vmimagemanger.pg and SGE

%prep

%setup -c

%build
make install prefix=%{buildroot}%{prefix}

%files
%defattr(-,root,root)
%{prefix}/share/doc/%{name}/README
%{prefix}/sbin/vsi_s_epilog.sh
%{prefix}/sbin/vsi_s_prolog.sh
%{prefix}/sbin/vsi_s_starter.sh
%{prefix}/sbin/vsi_v_start.sh
%{prefix}/sbin/vsi_v_stop.sh

%clean
rm -rf $RPM_BUILD_ROOT

