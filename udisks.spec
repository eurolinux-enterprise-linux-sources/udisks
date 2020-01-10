%define glib2_version           2.6.0
%define dbus_version            1.2
%define dbus_glib_version       0.82
%define polkit_version          0.92
%define parted_version          1.8.8
%define udev_version            145
%define mdadm_version           2.6.7
%define device_mapper_version   1.02
%define libatasmart_version     0.12
%define sg3_utils_version       1.27
%define smp_utils_version       0.94

Summary: Storage Management Service
Name: udisks
Version: 1.0.1
Release: 9%{?dist}
License: GPLv2+
Group: System Environment/Libraries
URL: http://www.freedesktop.org/wiki/Software/udisks
Source0: http://hal.freedesktop.org/releases/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: dbus-devel  >= %{dbus_version}
BuildRequires: dbus-glib-devel >= %{dbus_glib_version}
BuildRequires: polkit-devel >= %{polkit_version}
BuildRequires: parted-devel >= %{parted_version}
BuildRequires: device-mapper-devel >= %{device_mapper_version}
BuildRequires: intltool
BuildRequires: libatasmart-devel >= %{libatasmart_version}
BuildRequires: libgudev1-devel >= %{udev_version}
BuildRequires: libudev-devel >= %{udev_version}
BuildRequires: sg3_utils-devel >= %{sg3_utils_version}
BuildRequires: device-mapper-devel
# needed to pull in the system bus daemon
Requires: dbus >= %{dbus_version}
# needed to pull in the udev daemon
Requires: udev >= %{udev_version}
# we need at least this version for bugfixes / features etc.
Requires: libatasmart >= %{libatasmart_version}
Requires: mdadm >= %{mdadm_version}
# for smp_rep_manufacturer
Requires: smp_utils >= %{smp_utils_version}
# for mount, umount, mkswap
Requires: util-linux-ng
# for mkfs.ext3, mkfs.ext3, e2label
Requires: e2fsprogs
# for mkfs.xfs, xfs_admin
# Requires: xfsprogs
# for mkfs.vfat
Requires: dosfstools
# for mlabel
Requires: mtools

Patch1: udisks-1.0.1-disable-dm-watch.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1070147
# EMBARGOED CVE-2014-0004 udisks: udisks and udisks2: stack-based buffer overflow when handling long path names [rhel-6.6]
Patch2: buffer-overflow.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=673102
# [RFE] Make read-only mount of removable media enforceable
# https://bugs.freedesktop.org/show_bug.cgi?id=33461
Patch3: udisks-add-udev-mount-options-take-3.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1121742
# External storage device mounts can get force umounted during testing involving adapter removes and adds
Patch4: udisks-dm-suspended-noremove.patch

# for /proc/self/mountinfo, only available in 2.6.26 or higher
Conflicts: kernel < 2.6.26

# Obsolete and Provide DeviceKit-disks - udisks provides exactly the same
# ABI just with a different name and versioning-scheme
#
Obsoletes: DeviceKit-disks <= 009
Provides: DeviceKit-disks = 010

%description
udisks provides a daemon, D-Bus API and command line tools
for managing disks and storage devices.

%package devel
Summary: D-Bus interface definitions for udisks
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: gtk-doc

# See comment above
#
Obsoletes: DeviceKit-disks-devel <= 009
Provides: DeviceKit-disks-devel = 010

%description devel
D-Bus interface definitions for udisks.

%package devel-docs
Summary: Documentation for D-Bus interface of udisks
Group: Development/Libraries
Requires: %{name}-devel = %{version}-%{release}
BuildArch: noarch

%description devel-docs
D-Bus interface documentation for udisks.

%prep
%setup -q
%patch1 -p1 -b .disable-dm-watch
%patch2 -p1 -b .buffer-overflow
%patch3 -p1 -b .add-udev-mount-options
%patch4 -p1 -b .dm-suspended-noremove

%build
%configure --enable-gtk-doc --disable-lvm2 --disable-dmmp --disable-remote-access
make

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a

rm -f $RPM_BUILD_ROOT%{_libdir}/polkit-1/extensions/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/polkit-1/extensions/*.a

# TODO: should be fixed upstream
chmod 0644 $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/udisks-bash-completion.sh

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root,-)

%doc README AUTHORS NEWS COPYING HACKING doc/TODO

%{_sysconfdir}/dbus-1/system.d/*.conf
%{_sysconfdir}/profile.d/*.sh
/lib/udev/rules.d/*.rules

/lib/udev/udisks-part-id
/lib/udev/udisks-dm-export
/lib/udev/udisks-probe-ata-smart
/lib/udev/udisks-probe-sas-expander
/sbin/umount.udisks

%{_bindir}/*
%{_libexecdir}/*

%{_mandir}/man1/*
%{_mandir}/man7/*
%{_mandir}/man8/*

%{_datadir}/polkit-1/actions/*.policy

%{_libdir}/polkit-1/extensions/*.so

%{_datadir}/dbus-1/system-services/*.service

%attr(0700,root,root) %dir %{_localstatedir}/run/udisks
%attr(0700,root,root) %dir %{_localstatedir}/lib/udisks

%files devel
%defattr(-,root,root,-)

%{_datadir}/dbus-1/interfaces/*.xml
%{_datadir}/pkgconfig/udisks.pc

%files devel-docs
%defattr(-,root,root,-)

%dir %{_datadir}/gtk-doc/html/udisks
%{_datadir}/gtk-doc/html/udisks/*

# Note: please don't forget the %{?dist} in the changelog. Thanks
#
%changelog
* Wed Mar 04 2015 Tomas Smetana <tsmetana@redhat.com> - 1.0.1-9%{?dist}
- Improve patch for #1121742
- Related: rhbz#1121742

* Thu Feb 19 2015 Tomas Bzatek <tbzatek@redhat.com> - 1.0.1-8%{?dist}
- Allow extra mount options from udev rules (#673102, #681875)
- Do not force-unmount devices marked as DM_SUSPENDED (#1121742)

* Wed Mar 12 2014 Huzaifa Sidhpurwala <huzaifas@redhat.com> - 1.0.1-7%{?dist}
- Make sure doc subpackage is noarch

* Tue Mar 11 2014 Zeeshan Ali <zeenix@redhat.com> - 1.0.1-6%{?dist}
- Put devel-docs in a separate package (related: rhbz#11070147) .

* Mon Mar 11 2014 Zeeshan Ali <zeenix@redhat.com> - 1.0.1-5%{?dist}
- Related: rhbz#1070147.

* Thu Oct 13 2011 David Zeuthen <davidz@redhat.com> - 1.0.1-4%{?dist}
- Rebuild
- Related: rhbz#738479

* Tue Oct 11 2011 David Zeuthen <davidz@redhat.com> - 1.0.1-3%{?dist}
- Remove watch rule for DM devices
- Related: rhbz#738479

* Tue Sep  7 2010 Dennis Gregorovic <dgregor@redhat.com> - 1.0.1-2%{?dist}
- Remove requirement on xfsprogs
- Related: rhbz#630986

* Fri Apr 09 2010 David Zeuthen <davidz@redhat.com> - 1.0.1-1%{?dist}
- Update to 1.0.1 (CVE-2010-1149, #580007)
- Related: rhbz#580007

* Mon Mar 22 2010 David Zeuthen <davidz@redhat.com> - 1.0.0-2%{?dist}
- Don't BR lvm2-devel, we only need device-mapper-devel for libdevmapper
- Related: rhbz#575889

* Mon Mar 22 2010 David Zeuthen <davidz@redhat.com> - 1.0.0-1%{?dist}
- Update to release 1.0.0
- Build without LVM2 and Multipath support for now (#548870, #548874)
- Related: rhbz#575889

* Tue Feb 23 2010 David Zeuthen <davidz@redhat.com> - 1.0.0-0.git20100223.1%{?dist}
- Update to git snapshot for LVM2/Multipath support
- Bump lvm2 version requirement to 2.02.61
- Don't include compat devkit-disks symlinks
- Don't advertise remote access support via Avahi
- Related: rhbz#548874
- Related: rhbz#548870

* Fri Feb 19 2010 David Zeuthen <davidz@redhat.com> - 1.0.0-0.git20100115.3%{?dist}
- Rebuild without NTFS support
- Related: rhbz#566737

* Fri Jan 15 2010 David Zeuthen <davidz@redhat.com> - 1.0.0-0.git20100115.2%{?dist}
- Rebuild
- Related: rhbz#543948

* Fri Jan 15 2010 David Zeuthen <davidz@redhat.com> - 1.0.0-0.git20100115.1%{?dist}
- New git snapshot with LVM support (#548870)
- Related: rhbz#543948

* Tue Jan 12 2010 David Zeuthen <davidz@redhat.com> - 1.0.0-0.git20091202.3%{?dist}
- Rebuild
- Related: rhbz#543948

* Mon Dec 07 2009 David Zeuthen <davidz@redhat.com> - 1.0.0-0.git20091202.2%{?dist}
- Rebuild

* Fri Dec 04 2009 David Zeuthen <davidz@redhat.com> - 1.0.0-0.git20091202.1%{?dist}
- Updated for package review (#543608)

* Wed Dec 02 2009 David Zeuthen <davidz@redhat.com> - 1.0.0-0.git20091202%{?dist}
- Git snapshot for upcoming 1.0.0 release
