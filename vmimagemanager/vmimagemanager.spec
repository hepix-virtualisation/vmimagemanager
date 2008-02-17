Summary: vmimagemanager
Name: vmimagemanager
Version: 0.0.2
Vendor: Yokel
Release: 0
License: MPL
Group: virtulisation
Source: %{name}.src.tgz
BuildArch: noarch
Prefix:	/
BuildRoot: %{_tmppath}/%{name}-%{version}-build
Packager: o.m.synge@rl.ac.uk

%description
xen-image-manager is a generic image manager.

%prep

%setup -c

%build
echo "configdir"=%{prefix}/etc/%{name}/* >> /tmp/log
python setup.py  install  --root %{buildroot} --install-base %{prefix}

%files
%defattr(-,root,root)
%{prefix}/bin/*
%{prefix}/etc/%{name}/*
%{prefix}/usr/share/doc/%{name}/*


%clean
rm -rf $RPM_BUILD_ROOT

