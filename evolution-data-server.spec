%define use_nss 1
%define ldap_support 1
%define static_ldap 1
%define krb5_support 1
%define nntp_support 1

%define glib2_version 2.16.1
%define gtk2_version 2.14.0
%define gtk_doc_version 1.9
%define intltool_version 0.35.5
%define libbonobo_version 2.20.3
%define libgweather_version 2.25.4
%define libical_version 0.43
%define orbit2_version 2.9.8
%define soup_version 2.3.0
%define sqlite_version 3.5

%define eds_base_version 2.28
%define eds_api_version 1.2

%define use_gnome_keyring 1
%define support_imap4_provider 0

%define camel_provider_dir %{_libdir}/evolution-data-server-%{eds_api_version}/camel-providers
%define eds_extensions_dir %{_libdir}/evolution-data-server-%{eds_api_version}/extensions

### Abstract ###

Name: evolution-data-server
Version: 2.28.3
Release: 10%{?dist}
Group: System Environment/Libraries
Summary: Backend data server for Evolution
License: LGPLv2+
URL: http://projects.gnome.org/evolution/
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Source: http://download.gnome.org/sources/%{name}/2.28/%{name}-%{version}.tar.bz2

Provides: evolution-webcal = %{version}
Obsoletes: evolution-webcal < 2.24.0

### Patches ###

# RH bug #215702 / GNOME bug #487988
Patch10: evolution-data-server-1.8.0-fix-ldap-query.patch

# GNOME bug #373146
Patch11: evolution-data-server-1.10.1-camel-folder-summary-crash.patch

# RH bug #243296
Patch12: evolution-data-server-1.11.5-fix-64bit-acinclude.patch

# This makes our 2.28.3 equivalent to upstream's 2.28.3.1.
Patch13: evolution-data-server-2.28.3-remove-imap-debug-spew.patch

# RH bug #576215 / GNOME bug #613639
Patch14: eds-dir-prefix.patch

# RH bug #589192
Patch15: evolution-data-server-2.28.3-el6-translation-updates.patch

# RH bug #553556 / GNOME bug #601535
Patch16: evolution-data-server-2.28.3-unlocalized-categories.patch

# RH bug #605320 / GNOME bug #550622 & GNOME bug #604305
Patch17: evolution-data-server-2.28.3-imap-attachment-flag.patch

# RH bug #609024 / GNOME bug #550414
Patch18: evolution-data-server-2.28.3-summary-mismatch.patch

# RH bug #619286
Patch19: evolution-data-server-2.28.3-name-selector-entry.patch

### Build Dependencies ###

BuildRequires: GConf2-devel
BuildRequires: ORBit2-devel >= %{orbit2_version}
BuildRequires: bison
BuildRequires: db4-devel
BuildRequires: gettext
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: gnome-common
BuildRequires: gnutls-devel
BuildRequires: gtk-doc >= %{gtk_doc_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: intltool >= %{intltool_version}
BuildRequires: libbonobo-devel >= %{libbonobo_version}
BuildRequires: libglade2-devel
BuildRequires: libgweather-devel >= %{libgweather_version}
BuildRequires: libical-devel >= %{libical_version}
BuildRequires: libsoup-devel >= %{soup_version}
BuildRequires: libtool
BuildRequires: sqlite-devel >= %{sqlite_version}

%if %{use_nss}
BuildRequires: nspr-devel
BuildRequires: nss-devel
%else
BuildRequires: openssl-devel
%endif

%if %{ldap_support}
%if %{static_ldap}
BuildRequires: openldap-evolution-devel
BuildRequires: openssl-devel
%else
BuildRequires: openldap-devel >= 2.0.11 
%endif
%endif

%if %{krb5_support} 
BuildRequires: krb5-devel 
# tweak for krb5 1.2 vs 1.3
%define krb5dir /usr/kerberos
#define krb5dir `pwd`/krb5-fakeprefix
%endif

%description
The %{name} package provides a unified backend
for programs that work with contacts, tasks, and calendar information.

It was originally developed for Evolution (hence the name), but is now used
by other packages.

%package devel
Summary: Development files for building against %{name}
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: %{name}-doc = %{version}-%{release}
Requires: libbonobo-devel
Requires: libgweather-devel
Requires: libical-devel
Requires: libsoup-devel
Requires: sqlite-devel

%description devel
Development files needed for building things which link against %{name}.

%package doc
Summary: Documentation files for %{name}
Group: Development/Libraries
BuildArch: noarch

%description doc
This package contains developer documentation for %{name}.

%prep
%setup -q

%patch10 -p1 -b .fix-ldap-query
%patch11 -p1 -b .camel-folder-summary-crash
%patch12 -p1 -b .fix-64bit-acinclude
%patch13 -p1 -b .remove-imap-debug-spew
%patch14 -p1 -b .eds-dir-prefix
%patch15 -p1 -b .el6-translation-updates
%patch16 -p1 -b .unlocalized-categories
%patch17 -p1 -b .imap-attachment-flag
%patch18 -p1 -b .summary-mismatch
%patch19 -p1 -b .name-selector-entry

mkdir -p krb5-fakeprefix/include
mkdir -p krb5-fakeprefix/lib
mkdir -p krb5-fakeprefix/%{_lib}

%build
%if %{ldap_support}

%if %{static_ldap}
%define ldap_flags --with-openldap=%{_libdir}/evolution-openldap --with-static-ldap
# Set LIBS so that configure will be able to link with static LDAP libraries,
# which depend on Cyrus SASL and OpenSSL.  XXX Is the "else" clause necessary?
if pkg-config openssl ; then
	export LIBS="-lsasl2 `pkg-config --libs openssl`"
else
	export LIBS="-lsasl2 -lssl -lcrypto"
fi
%else
%define ldap_flags --with-openldap=yes
%endif

%else
%define ldap_flags --without-openldap
%endif

%if %{krb5_support}
%define krb5_flags --with-krb5=%{krb5dir}
%else
%define krb5_flags --without-krb5
%endif

%if %{nntp_support}
%define nntp_flags --enable-nntp=yes
%else
%define nntp_flags --enable-nntp=no
%endif

%if %{use_nss}
%define ssl_flags --enable-nss=yes --enable-smime=yes
%else
%define ssl_flags --enable-openssl=yes
%endif

%if %{use_nss}
if ! pkg-config --exists nss; then 
  echo "Unable to find suitable version of nss to use!"
  exit 1
fi
%endif

%if %{use_gnome_keyring}
%define keyring_flags --enable-gnome-keyring
%else
%define keyring flags --disable-gnome-keyring
%endif

%if %{support_imap4_provider}
%define imap4_flags --enable-imap4=yes
%else
%define imap4_flags --enable-imap4=no
%endif

export CPPFLAGS="-I%{_includedir}/et"
export CFLAGS="$RPM_OPT_FLAGS -DLDAP_DEPRECATED -fPIC -I%{_includedir}/et -fno-strict-aliasing"
%if ! %{use_nss}
if pkg-config openssl ; then
	CFLAGS="$CFLAGS `pkg-config --cflags openssl`"
	LDFLAGS="$LDFLAGS `pkg-config --libs-only-L openssl`"
fi
%endif

# Regenerate configure to pick up configure.in and acinclude.m4 changes.
aclocal -I m4
autoheader
automake
libtoolize
intltoolize --force
autoconf

# See Ross Burton's blog entry for why we want --with-libdb.
# http://www.burtonini.com/blog//computers/eds-libdb-2006-07-18-10-40

%configure \
	--with-libdb=/usr \
	--enable-file-locking=fcntl \
	--enable-dot-locking=no \
	--enable-gtk-doc \
	%ldap_flags %krb5_flags %nntp_flags %ssl_flags %imap4_flags \
	%keyring_flags
export tagname=CC
make %{?_smp_mflags} LIBTOOL=/usr/bin/libtool

%install
rm -rf $RPM_BUILD_ROOT
export tagname=CC
make DESTDIR=$RPM_BUILD_ROOT LIBTOOL=/usr/bin/libtool install

# remove libtool archives for importers and the like
find $RPM_BUILD_ROOT/%{_libdir} -name '*.la' -exec rm {} \;
rm -f $RPM_BUILD_ROOT/%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/evolution-data-server-%{eds_api_version}/camel-providers/*.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/evolution-data-server-%{eds_api_version}/extensions/*.a

# give the libraries some executable bits 
find $RPM_BUILD_ROOT -name '*.so.*' -exec chmod +x {} \;

%find_lang %{name}-%{eds_base_version}

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -f %{name}-%{eds_base_version}.lang
%defattr(-,root,root,-)
%doc README COPYING ChangeLog NEWS AUTHORS
%{_libdir}/bonobo/servers/GNOME_Evolution_DataServer_%{eds_api_version}.server
%{_libdir}/libcamel-%{eds_api_version}.so.*
%{_libdir}/libcamel-provider-%{eds_api_version}.so.*
%{_libdir}/libebackend-%{eds_api_version}.so.*
%{_libdir}/libebook-%{eds_api_version}.so.*
%{_libdir}/libecal-%{eds_api_version}.so.*
%{_libdir}/libedata-book-%{eds_api_version}.so.*
%{_libdir}/libedata-cal-%{eds_api_version}.so.*
%{_libdir}/libedataserver-%{eds_api_version}.so.*
%{_libdir}/libedataserverui-%{eds_api_version}.so.*
%{_libdir}/libegroupwise-%{eds_api_version}.so.*
%{_libdir}/libexchange-storage-%{eds_api_version}.so.*
%{_libdir}/libgdata-%{eds_api_version}.so.*
%{_libdir}/libgdata-google-%{eds_api_version}.so.*

%{_libexecdir}/evolution-data-server-%{eds_base_version}
%{_libexecdir}/camel-index-control-%{eds_api_version}
%{_libexecdir}/camel-lock-helper-%{eds_api_version}
%{_datadir}/evolution-data-server-%{eds_base_version}
%{_datadir}/idl/evolution-data-server-%{eds_api_version}
%{_datadir}/pixmaps/evolution-data-server
%dir %{_libdir}/evolution-data-server-%{eds_api_version}
%dir %{camel_provider_dir}
%dir %{eds_extensions_dir}

# Camel providers:
%{camel_provider_dir}/libcamelgroupwise.so
%{camel_provider_dir}/libcamelgroupwise.urls

%{camel_provider_dir}/libcamelimap.so
%{camel_provider_dir}/libcamelimap.urls

%if %{support_imap4_provider}
%{camel_provider_dir}/libcamelimap4.so
%{camel_provider_dir}/libcamelimap4.urls
%endif

%{camel_provider_dir}/libcamellocal.so
%{camel_provider_dir}/libcamellocal.urls

%{camel_provider_dir}/libcamelnntp.so
%{camel_provider_dir}/libcamelnntp.urls

%{camel_provider_dir}/libcamelpop3.so
%{camel_provider_dir}/libcamelpop3.urls

%{camel_provider_dir}/libcamelsendmail.so
%{camel_provider_dir}/libcamelsendmail.urls

%{camel_provider_dir}/libcamelsmtp.so
%{camel_provider_dir}/libcamelsmtp.urls

# e-d-s extensions:
%{eds_extensions_dir}/libebookbackendfile.so
%{eds_extensions_dir}/libebookbackendgoogle.so
%{eds_extensions_dir}/libebookbackendgroupwise.so
%{eds_extensions_dir}/libebookbackendldap.so
%{eds_extensions_dir}/libebookbackendvcf.so
%{eds_extensions_dir}/libebookbackendwebdav.so
%{eds_extensions_dir}/libecalbackendcaldav.so
%{eds_extensions_dir}/libecalbackendcontacts.so
%{eds_extensions_dir}/libecalbackendfile.so
%{eds_extensions_dir}/libecalbackendgoogle.so
%{eds_extensions_dir}/libecalbackendgroupwise.so
%{eds_extensions_dir}/libecalbackendhttp.so
%{eds_extensions_dir}/libecalbackendweather.so

%files devel
%defattr(-,root,root,-)
%{_includedir}/evolution-data-server-%{eds_base_version}
%{_libdir}/libcamel-%{eds_api_version}.so
%{_libdir}/libcamel-provider-%{eds_api_version}.so
%{_libdir}/libebackend-%{eds_api_version}.so
%{_libdir}/libebook-%{eds_api_version}.so
%{_libdir}/libecal-%{eds_api_version}.so
%{_libdir}/libedata-book-%{eds_api_version}.so
%{_libdir}/libedata-cal-%{eds_api_version}.so
%{_libdir}/libedataserver-%{eds_api_version}.so
%{_libdir}/libedataserverui-%{eds_api_version}.so
%{_libdir}/libegroupwise-%{eds_api_version}.so
%{_libdir}/libexchange-storage-%{eds_api_version}.so
%{_libdir}/libgdata-%{eds_api_version}.so
%{_libdir}/libgdata-google-%{eds_api_version}.so
%{_libdir}/pkgconfig/camel-%{eds_api_version}.pc
%{_libdir}/pkgconfig/camel-provider-%{eds_api_version}.pc
%{_libdir}/pkgconfig/evolution-data-server-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libebackend-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libebook-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libecal-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libedata-book-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libedata-cal-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libedataserver-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libedataserverui-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libegroupwise-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libexchange-storage-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libgdata-%{eds_api_version}.pc
%{_libdir}/pkgconfig/libgdata-google-%{eds_api_version}.pc

%files doc
%defattr(-,root,root,-)
%{_datadir}/gtk-doc/html/camel
%{_datadir}/gtk-doc/html/libebackend
%{_datadir}/gtk-doc/html/libebook
%{_datadir}/gtk-doc/html/libecal
%{_datadir}/gtk-doc/html/libedata-book
%{_datadir}/gtk-doc/html/libedata-cal
%{_datadir}/gtk-doc/html/libedataserver
%{_datadir}/gtk-doc/html/libedataserverui

%changelog
* Wed Aug 04 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.3-10.el6
- Add patch for RH bug #619286 (IM malfunction in To/CC fields).

* Tue Jun 29 2010 Milan Crha <mcrha@redhat.com> - 2.28.3-9.el6
- Add patch for RH bug #609024 ("Summary and folder mismatch" error).

* Tue Jun 29 2010 Milan Crha <mcrha@redhat.com> - 2.28.3-8.el6
- Update patch for RH bug #605320 (with patch from GNOME bug #604305).

* Wed Jun 23 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.3-7.el6
- Add patch for RH bug #605320 (some IMAP msgs missing attachment flag).

* Fri Jun 18 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.3-6.el6
- Add patch for RH bug #553556 (unlocalized categories).

* Fri Jun 11 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.3-5.el6
- Translation updates for Red Hat Supported Languages (RH bug #589192).

* Thu May 20 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.3-4.el6
- Add -fno-strict-aliasing to CFLAGS.
- Actually apply the directory prefix patch.

* Tue Mar 23 2010 Ray Strode <rstrode@redhat.com> 2.28.3-3.el6
Resolves: #576215
- Make .gnome2_private relocatable

* Tue Mar 02 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.3-2.el6
- Remove debug spew from IMAP provider.

* Tue Mar 02 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.3-1.el6
- Update to 2.28.3

* Tue Jan 12 2010 Milan Crha <mcrha@redhat.com> - 2.28.2-4.el6
- Wrap package description to fit within line bounds

* Tue Jan 12 2010 Milan Crha <mcrha@redhat.com> - 2.28.2-3.el6
- Remove unneeded requirements

* Tue Jan 12 2010 Milan Crha <mcrha@redhat.com> - 2.28.2-2.el6
- Correct Source URL

* Mon Jan 04 2010 Milan Crha <mcrha@redhat.com> - 2.28.2-1.el6
- Update to 2.28.2

* Mon Oct 19 2009 Milan Crha <mcrha@redhat.com> - 2.28.1-1.fc12
- Update to 2.28.1

* Mon Sep 21 2009 Milan Crha <mcrha@redhat.com> - 2.28.0-1.fc12
- Update to 2.28.0

* Mon Sep 07 2009 Milan Crha <mcrha@redhat.com> - 2.27.92-1.fc12
- Update to 2.27.92

* Thu Aug 27 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.91-3.fc12
- Rebuild with old OpenSSL, er something...

* Thu Aug 27 2009 Tomas Mraz <tmraz@redhat.com> - 2.27.91-2.fc12
- rebuilt with new openssl

* Mon Aug 24 2009 Milan Crha <mcrha@redhat.com> - 2.27.91-1.fc12
- Update to 2.27.91

* Mon Aug 10 2009 Milan Crha <mcrha@redhat.com> - 2.27.90-1.fc12
- Update to 2.27.90

* Mon Jul 27 2009 Milan Crha <mcrha@redhat.com> - 2.27.5-1.fc12
- Update to 2.27.5

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 13 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.4-1.fc12
- Update to 2.27.4
- Remove patch for RH bug #505661 (fixed upstream).

* Thu Jul 02 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.3-3.fc12
- Add patch for RH bug #505661 (crash on startup).

* Wed Jul 01 2009 Milan Crha <mcrha@redhat.com> - 2.27.3-2.fc12
- Rebuild against newer gcc

* Mon Jun 15 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.3-1.fc12
- Update to 2.27.3

* Mon May 25 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.2-1.fc12
- Update to 2.27.2
- Remove strict_build_settings since the settings are used upstream now.

* Mon May 04 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.1-1.fc12
- Update to 2.27.1
- Bump evo_major to 2.28.

* Wed Apr 15 2009 Matthew Barnes <mbarnes@redhat.com> - 2.26.1.1-1.fc11
- Update to 2.26.1.1

* Mon Apr 13 2009 Matthew Barnes <mbarnes@redhat.com> - 2.26.1-1.fc11
- Update to 2.26.1

* Mon Mar 16 2009 Matthew Barnes <mbarnes@redhat.com> - 2.26.0-1.fc11
- Update to 2.26.0
- Remove patch for RH bug #568332 (fixed upstream).
- Remove patch for GNOME bug #573240 (reverted upstream).

* Fri Mar 13 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.92-4.fc11
- Revise patch for RH bug #568332 to match upstream commit.

* Thu Mar 12 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.92-3.fc11
- Add patch for RH bug #568332 (thread leak in fsync() rate limiting).

* Sat Mar 07 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.92-2.fc11
- Add patch to revert GNOME bug #573240 (IMAP message loading regressions).

* Mon Mar 02 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.92-1.fc11
- Update to 2.25.92

* Tue Feb 24 2009 Matthias Clasen <mclasen@redhat.com> 2.25.91-3
- Make -doc noarch

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.91-1.fc11
- Update to 2.25.91

* Fri Feb 06 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.90-5.fc11
- Update BuildRoot, License, Source and URL tags.
- Require gnome-common so we don't have to patch it out.

* Wed Feb 04 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.90-4.fc11
- ... and fix our own <ical.h> includes too.

* Wed Feb 04 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.90-3.fc11
- Work around libical's broken pkg-config file.

* Mon Feb 02 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.90-2.fc11
- Forgot the libical requirement in devel subpackage.

* Mon Feb 02 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.90-1.fc11
- Update to 2.25.90
- Add libical build requirement.

* Mon Jan 19 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.5-1.fc11
- Update to 2.25.5
- Bump gtk2_version to 2.14.0.

* Fri Jan 16 2009 Tomas Mraz <tmraz@redhat.com> - 2.25.4-2.fc11
- rebuild with new openssl

* Mon Jan 05 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.4-1.fc11
- Update to 2.25.4

* Mon Dec 15 2008 Matthew Barnes <mbarnes@redhat.com> - 2.25.3-1.fc11
- Update to 2.25.3
- New BR: libgweather-devel

* Thu Dec 04 2008 Matthew Barnes <mbarnes@redhat.com> - 2.25-2-2.fc11
- Rebuild due to recent pkg-config breakage.

* Mon Dec 01 2008 Matthew Barnes <mbarnes@redhat.com> - 2.25.2-1.fc11
- Update to 2.25.2

* Thu Nov 27 2008 Matthew Barnes <mbarnes@redhat.com> - 2.25.1-2.fc11
- Obsolete the evolution-webcal package (RH bug #468855).

* Mon Nov 03 2008 Matthew Barnes <mbarnes@redhat.com> - 2.25.1-1.fc11
- Update to 2.25.1
- Bump eds_base_version to 2.26.
- Remove patch for RH bug #467804 (fixed upstream).

* Thu Oct 23 2008 Matthew Barnes <mbarnes@redhat.com> - 2.24.1-2.fc10
- Add patch for RH bug #467804 (remove console spew).

* Tue Oct 21 2008 Matthew Barnes <mbarnes@redhat.com> - 2.24.1-1.fc10
- Update to 2.24.1

* Mon Sep 22 2008 Matthew Barnes <mbarnes@redhat.com> - 2.24.0-1.fc10
- Update to 2.24.0

* Mon Sep 08 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.92-1.fc10
- Update to 2.23.92

* Mon Sep 01 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.91-1.fc10
- Update to 2.23.91

* Wed Aug 20 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.90.1-1.fc10
- Update to 2.23.90.1

* Mon Aug 04 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.6-3.fc10
- Add sqlite3 requirement to devel subpackage.

* Mon Aug 04 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.6-2.fc10
- Add sqlite3 to Camel's pkgconfig requirements.

* Mon Aug 04 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.6-1.fc10
- Update to 2.23.6
- Add build requirement for sqlite.

* Mon Jul 21 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.5-1.fc10
- Update to 2.23.5
- Remove patch for RH bug #534080 (fixed upstream).

* Fri Jul 18 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.23.4-3
- fix license tag

* Thu Jul 03 2008 Matthew Barnes <mbarnes@redhat.com> - 3.23.4-2.fc10
- Add patch for RH bug #534080 (fix attachment saving).

* Mon Jun 16 2008 Matthew Barnes <mbarnes@redhat.com> - 3.23.4-1.fc10
- Update to 2.23.4

* Mon Jun 02 2008 Matthew Barnes <mbarnes@redhat.com> - 3.23.3-1.fc10
- Update to 2.23.3
- Remove patch for GNOME bug #531439 (fixed upstream).

* Sun May 18 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.2-3.fc10
- Add patch for GNOME bug #531439 (GPG passphrases destroy passwords).

* Tue May 13 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.2-2.fc10
- Fix some third-party package breakage caused by libebackend.

* Mon May 12 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.2-1.fc10
- Update to 2.23.2
- Add files for new libebackend library.
- Remove patch for RH bug #202309 (fixed upstream).

* Mon Apr 21 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.1-1.fc10
- Update to 2.23.1
- Bump eds_base_version to 2.24.
- Bump glib2 requirement to 2.16.1.
- Drop gnome-vfs2 requirement.

* Mon Apr 07 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.1-1.fc9
- Update to 2.22.1
- Remove patch for RH bug #296671 (fixed upstream).
- Remove patch for GNOME bug #523023 (fixed upstream).

* Mon Mar 24 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.0-3.fc9
- Add patch for GNOME bug #523023 (EFolder leak in evo-ex-storage).

* Tue Mar 11 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.0-2.fc9
- Add patch for RH bug #296671 (GC servers may not support NTLM).

* Mon Mar 10 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.0-1.fc9
- Update to 2.22.0

* Mon Feb 25 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.92-1.fc9
- Update to 2.21.92
- Remove patch for GNOME bug #516074 (fixed upstream).

* Thu Feb 14 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.91-3.fc9
- Try removing the ancient "ldap-x86_64-hack" patch.

* Wed Feb 13 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.91-2.fc9
- Rebuild against libsoup 2.3.2.

* Mon Feb 11 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.91-1.fc9
- Update to 2.21.91
- Add patch for GNOME bug #516074 (latest glibc breaks Camel).

* Mon Jan 28 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.90-1.fc9
- Update to 2.21.90
- Remove patch for GNOME bug #509644 (fixed upstream).

* Thu Jan 17 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.5-3.fc9
- Rename evolution-1.4.4-ldap-x86_64-hack.patch to avoid namespace
  collision with similarly named patch in evolution (RH bug #395551).

* Wed Jan 16 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.5-2.fc9
- Add patch for GNOME bug #509644 (password dialog breakage).
- Remove patch for RH bug #384741 (fixed upstream).
- Remove patch for GNOME bug #363695 (obsolete).
- Remove patch for GNOME bug #376991 (obsolete).

* Mon Jan 14 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.5-1.fc9
- Update to 2.21.5

* Mon Dec 17 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.4-1.fc9
- Update to 2.21.4
- Require gtk-doc >= 1.9.

* Tue Dec  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.3-2
- Rebuild against openssl

* Mon Dec 03 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.3-1.fc9
- Update to 2.21.3

* Thu Nov 15 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.2-2.fc9
- Add patch for RH bug #384741 (authentication crash).

* Mon Nov 12 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.2-1.fc9
- Update to 2.21.2

* Mon Oct 29 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.1-1.fc9
- Update to 2.21.1
- Bump eds_base_version to 2.22.
- Remove patch for RH bug #212106 (fixed upstream).
- Remove patch for GNOME bug #417999 (fixed upstream).

* Fri Oct 26 2007 Matthew Barnes <mbarnes@redhat.com> - 1.12.1-4.fc9
- Remove the use_gtk_doc macro.
- Remove redundant requirements.
- Use the name tag where appropriate.
- Add an evolution-data-server-doc subpackage.

* Thu Oct 18 2007 Matthew Barnes <mbarnes@redhat.com> - 1.12.1-3.fc9
- Porting a couple patches over from RHEL5:
- Add patch for RH bug #212106 (address book error on fresh install).
- Add patch for RH bug #215702 (bad search filter for LDAP address books).

* Tue Oct 16 2007 Matthew Barnes <mbarnes@redhat.com> - 1.12.1-2.fc8
- Disable patch for GNOME bug #376991 for now.  It may be contributing
  to password prompting problems as described in RH bug #296671.

* Mon Oct 15 2007 Milan Crha <mcrha@redhat.com> - 1.12.1-1.fc8
- Update to 1.12.1

* Mon Sep 17 2007 Matthew Barnes <mbarnes@redhat.com> - 1.12.0-1.fc8
- Update to 1.12.0

* Mon Sep 03 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.92-1.fc8
- Update to 1.11.92

* Tue Aug 28 2007 Milan Crha <mcrha@redhat.com> - 1.11.91-1.fc8
- Update to 1.11.91
- Removed patch for RH bug #215634 (fixed upstream).
- Removed patch for GNOME bug #466987 (fixed upstream).

* Wed Aug 22 2007 Adam Jackson <ajax@redhat.com> 1.11.90-4.fc8
- Add Requires: glib2 >= 2.14.0, since it's in the buildroot now, and
  forcibly introduces deps on symbols that don't exist in 2.13.  If
  only we had working symbol versioning.

* Mon Aug 20 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.90-3.fc8
- Revise patch for GNOME bug #417999 to fix GNOME bug #447591
  (Automatic Contacts combo boxes don't work).

* Mon Aug 13 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.90-2.fc8
- Re-enable the --with-libdb configure option.

* Mon Aug 13 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.90-1.fc8
- Update to 1.11.90
- Add patch for GNOME bug #466987 (glibc redefines "open").
- Remove patch for GNOME bug #415891 (fixed upstream).

* Wed Aug 08 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.6.1-1.fc8
- Update to 1.11.6.1

* Tue Jul 31 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.6-1.fc8
- Update to 1.11.6
- Remove patch for GNOME bug #380534 (fixed upstream).

* Fri Jul 27 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.5-3.fc8
- Add patch for GNOME bug #380534 (clarify version requirements).

* Tue Jul 17 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.5-2.fc8
- Add patch for RH bug #243296 (fix LDAP configuration).

* Mon Jul 09 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.5-1.fc8
- Update to 1.11.5

* Mon Jun 18 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.4-1.fc8
- Update to 1.11.4
- Remove patch for RH bug #202309 (fixed upstream).
- Remove patch for GNOME bug #312854 (fixed upstream).
- Remove patch for GNOME bug #447414 (fixed upstream).

* Fri Jun 15 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.3-3.fc8
- Add patch for GNOME bug #224277 (Camel IMAP security flaw).

* Thu Jun 14 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.3-2.fc8
- Add patch for GNOME bug #312584 (renaming Exchange folders).

* Mon Jun 04 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.3-1.fc8
- Update to 1.11.3
- Remove patch for GNOME bug #415922 (fixed upstream).

* Thu May 31 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.2-3.fc8
- Revise patch for GNOME bug #376991 to fix RH bug #241974.

* Mon May 21 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.2-2.fc8
- Store account passwords in GNOME Keyring.

* Fri May 18 2007 Matthew Barnes <mbarnes@redhat.com> - 1.11.2-1.fc8
- Update to 1.11.2
- Bump eds_base_version to 1.12.
- Add patch to fix implicit function declarations.
- Remove patch for RH bug #203058 (fixed upstream).
- Remove patch for RH bug #210142 (fixed upstream).
- Remove patch for RH bug #235290 (fixed upstream).
- Remove patch for GNOME bug #360240 (fixed upstream).
- Remove patch for GNOME bug #360619 (fixed upstream).
- Remove patch for GNOME bug #373117 (fixed upstream).
- Revise patch for GNOME bug #415891 (partially fixed upstream).

* Wed May 09 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.1-6.fc7
- Add patch for RH bug #215634 (read NSS certificates more reliably).

* Tue May 08 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.1-5.fc7
- Add patch for GNOME bug #373146 (spam message triggers crash).

* Mon May 07 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.1-4.fc7
- Add patch to fix a dangling pointer in e-source-group.c.

* Mon Apr 30 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.1-3.fc7
- Revise patch for RH bug #235290 to not break string freeze.

* Tue Apr 24 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.1-2.fc7
- Add patch for RH bug #235290 (APOP authentication vulnerability).

* Mon Apr 09 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.1-1.fc7
- Update to 1.10.1
- Remove evolution-data-server-1.10.0-no-more-beeps.patch (fixed upstream).

* Wed Apr 04 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.0-6.fc7
- Revise patch for GNOME bug #417999 (another ESourceComboBox goof).

* Mon Apr 02 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.0-5.fc7
- Make the new ESourceComboBox widget work properly (RH bug #234760).

* Tue Mar 27 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.0-4.fc7
- Link to static evolution-openldap library (RH bug #210126).
- Require openssl-devel when statically linking against openldap.
- Add -Wdeclaration-after-statement to strict build settings.

* Thu Mar 22 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.0-3.fc7
- Stop beeping at me!

* Wed Mar 14 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.0-2.fc7
- Modify patch for GNOME bug #376991 to fix RH bug #231994.
- Add patch for GNOME bug #417999 (avoid deprecated GTK+ symbols).
- Remove evolution-data-server-1.0.2-workaround-cal-backend-leak.patch.
- Remove evolution-data-server-1.2.2-fix_open_calendar_declaration.patch.
- Remove evolution-data-server-1.3.8-fix-implicit-function-declarations.

* Mon Mar 12 2007 Matthew Barnes <mbarnes@redhat.com> - 1.10.0-1.fc7
- Update to 1.10.0
- Remove patch for GNOME bug #301363 (fixed upstream).

* Fri Mar 09 2007 Matthew Barnes <mbarnes@redhat.com> - 1.9.92-4.fc7
- Add patch for GNOME bug #415922 (support MS ISA Server 2004).
- Patch by Kenny Root.

* Thu Mar 08 2007 Matthew Barnes <mbarnes@redhat.com> - 1.9.92-3.fc7
- Add patch for GNOME bug #415891 (introduce EFlag API).
- Add patch for GNOME bug #376991 (refactor password handling).

* Tue Mar 06 2007 Matthew Barnes <mbarnes@redhat.com> - 1.9.92-2.fc7
- Add patch for GNOME bug #301363 (update timezones).

* Mon Feb 26 2007 Matthew Barnes <mbarnes@redhat.com> - 1.9.92-1.fc7
- Update to 1.9.92
- Remove patch for GNOME bug #356177 (fixed upstream).
- Add minimum version to intltool requirement (current >= 0.35.5).

* Mon Feb 12 2007 Matthew Barnes <mbarnes@redhat.com> - 1.9.91-1.fc7
- Update to 1.9.91
- Add flag to disable deprecated Pango symbols.
- Remove patch for GNOME bug #359979 (fixed upstream).

* Sun Jan 21 2007 Matthew Barnes <mbarnes@redhat.com> - 1.9.5-4.fc7
- Revise evolution-data-server-1.8.0-no-gnome-common.patch so that we no
  longer have to run autoconf before building.

* Wed Jan 10 2007 Matthew Barnes <mbarnes@redhat.com> - 1.9.5-3.fc7
- Add patch for GNOME bug #359979 (change EMsgPort semantics).

* Mon Jan 09 2007 Matthew Barnes <mbarnes@redhat.com> - 1.9.5-2.fc7
- Require libsoup-devel in devel subpackage (RH bug #152482).

* Mon Jan 08 2007 Matthew Barnes <mbarnes@redhat.com> - 1.9.5-1.fc7
- Update to 1.9.5
- Remove patch for GNOME bug #362638 (fixed upstream).
- Remove patch for GNOME bug #387638 (fixed upstream).

* Tue Dec 19 2006 Matthew Barnes <mbarnes@redhat.com> - 1.9.4-1.fc7
- Update to 1.9.4
- Add patch for GNOME bug #373117 (storing color settings).
- Add patch for GNOME bug #387638 (implicit function declaration).

* Mon Dec 04 2006 Matthew Barnes <mbarnes@redhat.com> - 1.9.3-1.fc7
- Update to 1.9.3
- Remove patch for GNOME bug #353924 (fixed upstream).

* Fri Nov 10 2006 Matthew Barnes <mbarnes@redhat.com> - 1.9.2-3.fc7
- Add patch for RH bug #210142 (calendar crash in indic locales).

* Wed Nov 08 2006 Matthew Barnes <mbarnes@redhat.com> - 1.9.2-2.fc7
- Add patch for RH bug #203058 (name selector dialog glitch).

* Mon Nov 06 2006 Matthew Barnes <mbarnes@redhat.com> - 1.9.2-1.fc7
- Update to 1.9.2
- Remove patch for Gnome.org bugs #369168, #369259, and #369261
  (fixed upstream).

* Thu Nov  2 2006 Matthew Barnes <mbarnes@redhat.com> - 1.9.1-4.fc7
- Add patch for Gnome.org bug #369168, #369259, and #369261
  (misc camel bugs reported by Hans Petter Jansson).

* Wed Nov  1 2006 Matthew Barnes <mbarnes@redhat.com> - 1.9.1-3.fc7
- Add patch for Gnome.org bug #353924 (category sorting).

* Fri Oct 27 2006 Matthew Barnes <mbarnes@redhat.com> - 1.9.1-2.fc7
- Rebuild

* Fri Oct 27 2006 Matthew Barnes <mbarnes@redhat.com> - 1.9.1-2.fc7
- Update to 1.9.1
- Add patch for Gnome.org bug #356177 (deprecate EMutex).
- Add patch for Gnome.org bug #363695 (deprecate EMemPool, EStrv, EPoolv).
- Remove Jerusalem.ics timezone file (fixed upstream).
- Remove patch for RH bug #198935 (fixed upstream).

* Mon Oct 16 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.1-1.fc7
- Update to 1.8.1
- Use stricter build settings.
- Add patch for Gnome.org bug #360240 ("unused variable" warnings).
- Add patch for Gnome.org bug #360619 ("incompatible pointer type" warnings).
- Add patch for Gnome.org bug #362638 (deprecate EThread).
- Remove patch for RH bug #198935 (fixed upstream).
- Remove patch for RH bug #205187 (fixed upstream).
- Remove patch for Gnome.org bug #353478 (fixed upstream).
- Remove patch for Gnome.org bug #356828 (fixed upstream).
- Remove patch for Gnome.org bug #357666 (fixed upstream).

* Tue Sep 26 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-11.fc6
- Add patch for RH bug #203915 (fix dangerous mallocs in camel).

* Mon Sep 25 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-10.fc6
- Add patch for Gnome.org bug #357666.

* Thu Sep 21 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-9.fc6
- Revise patch for RH bug #198935 (fix a crash reported in bug #207446).

* Wed Sep 20 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-8.fc6
- Revise patch for RH bug #198935 (fix a typo).

* Wed Sep 20 2006 Matthias Clasen <mclasen@redhat.com> - 1.8.0-7.fc6
- Fix the timezone info for Jerusalem  (#207161)

* Wed Sep 20 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-6.fc6
- Add patch for Gnome.org bug #356828 (lingering file on uninstall).

* Mon Sep 18 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-5.fc6
- Revise patch for RH bug #205187 (use upstream's version).

* Sat Sep 16 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-4.fc6
- Add patch for RH bug #205187 (crash on startup).

* Fri Sep 15 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-3.fc6
- Revise patch for RH bug #198935 to eliminate a race condition.

* Tue Sep 12 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-2.fc6
- Add patch for RH bug #198935.

* Mon Sep  4 2006 Matthew Barnes <mbarnes@redhat.com> - 1.8.0-1.fc6
- Update to 1.8.0
- Remove evolution-data-server-1.5.4-make_imap4_optional.patch (fixed upstream)
  and save remaining hunk as evolution-data-server-1.8.0-no-gnome-common.patch.
- Remove patch for RH bug #202329 (fixed upstream).
- Remove patch for Gnome.org bug #349847 (fixed upstream).

* Tue Aug 29 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.92-4.fc6
- Revise patch for RH bug #198935.
- Add patch for Gnome.org bug #353478.

* Mon Aug 28 2006 Ray Strode <rstrode@redhat.com> - 1.7.92-3.fc6
- Add patch from Veerapuram Varadhan to fix fd leak (bug 198935).

* Tue Aug 22 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.92-2
- Add patch for Gnome.org bug #349847.

* Mon Aug 21 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.92-1
- Update to 1.7.92

* Wed Aug 16 2006 Ray Strode <rstrode@redhat.com> - 1.7.91-3
- Add fix from Matthias Clasen that might help bug 202309.

* Mon Aug 14 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.91-2
- Add patch for RH bug #202329.

* Mon Aug  7 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.91-1
- Update to 1.7.91
- Remove patch for Gnome.org bug #348725 (fixed upstream).

* Fri Aug  4 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.90.1-5
- Update to 1.7.90.1 (again)

* Thu Aug  3 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.4-5
- Remove patches for Gnome.org bug #309079 (rejected upstream).
- One of these patches was causing RH bug #167157.

* Thu Aug  3 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.4-4
- No longer packaging unused patches.

* Mon Jul 31 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.4-3
- Revert to version 1.7.4 to prevent API/ABI breakage.
- Add back patch to make --with-libdb configure option work.

* Mon Jul 31 2006 Ray Strode <rstrode@redhat.com> - 1.7.90.1-4
- add executable bits to libs 

* Sun Jul 31 2006 Matthias Clasen <mclasen@redhat.com> - 1.7.90.1-3
- Rebuild

* Wed Jul 26 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.90.1-2
- Rebuild

* Tue Jul 25 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.90.1-1
- Update to 1.7.90.1
- Add patch for Gnome.org bug #348725.
- Remove patch to make --with-db configure option work (fixed upstream).

* Tue Jul 19 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.4-2
- Dynamically link to BDB.
- Add patch to make --with-db configure option work.
- Add Requires for db4 and BuildRequires for db4-devel.
- Clean up spec file, renumber patches.

* Wed Jul 12 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.4-1
- Update to 1.7.4
- Remove patch for Gnome.org bug #345965 (fixed upstream).

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.7.3-3.1
- rebuild

* Tue Jun 27 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.3-3
- Show GPG key name when asking for the password (Gnome.org #345965).

* Wed Jun 14 2006 Tomas Mraz <tmraz@redhat.com> - 1.7.3-2
- rebuilt with new gnutls

* Tue Jun 13 2006 Matthisa Clasen  <mclasen@redhat.com> 1.7.3-1
- Update to 1.7.3

* Thu Jun  8 2006 Jeremy Katz <katzj@redhat.com> - 1.7.2-3
- BR flex

* Sat May 27 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.2-2
- Add missing BuildRequires for gettext (#193360).

* Wed May 17 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.2
- Update to 1.7.2
- Remove evolution-data-server-1.7.1-nss_auto_detect.patch; in upstream now.

* Sun May 14 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.1-2
- Add temporary patch evolution-data-server-1.7.1-nss_auto_detect.patch
  to help `configure' detect the SSL modules (closes #191567).

* Wed May 10 2006 Matthew Barnes <mbarnes@redhat.com> - 1.7.1-1
- Update to 1.7.1
- Bump eds_base_version from 1.6 to 1.8.
- Disable evolution-data-server-1.2.0-validatehelo.patch (accepted upstream).

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 1.6.1-3
- Avoid a multilib conflict

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 1.6.1-2
- Update to 1.6.1

* Mon Mar 13 2006 Ray Strode <rstrode@redhat.com> - 1.6.0-1
- 1.6.0

* Mon Feb 27 2006 Ray Strode <rstrode@redhat.com> - 1.5.92-1
- 1.5.92

* Tue Feb 14 2006 David Malcolm <dmalcolm@redhat.com> - 1.5.91-1
- 1.5.91

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.5.90-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.5.90-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 31 2006 Ray Strode <rstrode@redhat.com> - 1.5.90-2
- add build deps (bug 137553)

* Mon Jan 30 2006 David Malcolm <dmalcolm@redhat.com> - 1.5.90-1
- 1.5.90
- explicitly list various files rather than rely on globbing
- enabled parallel make

* Wed Jan 25 2006 David Malcolm <dmalcolm@redhat.com> - 1.5.5-1
- 1.5.5
- added CalDAV backend to the list of packaged extensions

* Mon Jan  9 2006 David Malcolm <dmalcolm@redhat.com> - 1.5.4-4
- updated patch 300 to remove usage of GNOME_COMPILE_WARNINGS from configure.in
  (since gnome-common might not be available when we rerun the autotools)

* Mon Jan  9 2006 David Malcolm <dmalcolm@redhat.com> - 1.5.4-3
- added patch to make the "imap4"/"IMAP4rev1" backend optional; disable it in 
  our packages; re-run automake since we have touched various Makefile.am 
  files; rerun intltoolize to avoid incompatibilities between tarball copy of
  intltool-merge.in and intltool.m4 in intltool package (@EXPANDED_LIBDIR@
  renamed to @INTLTOOL_LIBDIR@) (#167574)
- explicitly list the camel providers and e-d-s extension files in the spec file

* Thu Jan  5 2006 David Malcolm <dmalcolm@redhat.com> - 1.5.4-2
- added patch from David Woodhouse to validate reverse DNS domain before using 
  in SMTP greeting (patch 103, #151121)

* Tue Jan  3 2006 David Malcolm <dmalcolm@redhat.com> - 1.5.4-1
- 1.5.4

* Mon Dec 19 2005 David Malcolm <dmalcolm@redhat.com> - 1.5.3-2
- Update specfile and patch 5 (evolution-data-server-1.3.5-nspr_fix.patch) to
  use nss rather than mozilla-nss throughout

* Mon Dec 19 2005 David Malcolm <dmalcolm@redhat.com> - 1.5.3-1
- 1.5.3

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Dec  6 2005 David Malcolm <dmalcolm@redhat.com> - 1.5.2-1
- 1.5.2
- bump eds_base_version from 1.4 to 1.6
- updated patch 102

* Mon Dec  5 2005 David Malcolm <dmalcolm@redhat.com> - 1.4.2.1-1
- 1.4.2.1

* Tue Nov 29 2005 David Malcolm <dmalcolm@redhat.com> - 1.4.2-1
- 1.4.2

* Tue Nov 29 2005 David Malcolm <dmalcolm@redhat.com> - 1.4.1.1-3
- add -DLDAP_DEPRECATED to CFLAGS (#172999)

* Thu Nov 10 2005 David Malcolm <dmalcolm@redhat.com> - 1.4.1.1-2
- Updated license field to reflect change from GPL to LGPL
- Remove all static libraries, not just those in /usr/lib; avoid listing libdir
  subdirectory so that we can be more explicit about the package payload (bug
  #172882)

* Mon Oct 17 2005 David Malcolm <dmalcolm@redhat.com> - 1.4.1.1-1
- 1.4.1.1

* Mon Oct 17 2005 David Malcolm <dmalcolm@redhat.com> - 1.4.1-2
- Updated patch 102 (fix-implicit-function-declarations) to include fix for 
  http calendar backend (thanks to Peter Robinson)

* Tue Oct  4 2005 David Malcolm <dmalcolm@redhat.com> - 1.4.1-1
- 1.4.1

* Wed Sep 14 2005 Jeremy Katz <katzj@redhat.com> - 1.4.0-2
- rebuild now that mozilla builds on ppc64

* Tue Sep  6 2005 David Malcolm <dmalcolm@redhat.com> - 1.4.0-1
- 1.4.0
- Removed evolution-data-server-1.3.8-fix-libical-vsnprintf.c.patch; a version
  of this is now upstream (was patch 103, added in 1.3.8-2)

* Wed Aug 31 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.8-6
- Use regular LDAP library for now, rather than evolution-openldap (#167238)

* Tue Aug 30 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.8-5
- Add -Werror-implicit-function-declaration back to CFLAGS at the make stage, 
  after the configure, to spot 64-bit problems whilst avoiding breaking 
  configuration tests; expand patch 102 to avoid this breaking libdb's CFLAGS

* Wed Aug 24 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.8-4
- Remove -Werror-implicit-function-declaration from CFLAGS; this broke the
  configuration test for fast mutexes in the internal copy of libdb, and hence
  broke access to local addressbooks (#166742)
- Introduce static_ldap macro; use it to link to static evolution-openldap 
  library, containing NTLM support for LDAP binds (needed by Exchange support)

* Tue Aug 23 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.8-3
- Updated patch 102 to fix further implicit function declarations

* Tue Aug 23 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.8-2
- added patch (103) to fix problem with configuration macros in libical's
  vsnprintf.c

* Tue Aug 23 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.8-1
- 1.3.8
- Add -Werror-implicit-function-declaration to CFLAGS, to avoid 64-bit issues
  and add patch to fix these where they occur (patch 102)

* Mon Aug 15 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.7-2
- rebuild

* Tue Aug  9 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.7-1
- 1.3.7

* Mon Aug  8 2005 Tomas Mraz <tmraz@redhat.com> - 1.3.6.1-2
- rebuild with new gnutls

* Fri Jul 29 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.6.1-1
- 1.3.6.1

* Thu Jul 28 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.6-1
- 1.3.6

* Mon Jul 25 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.5-2
- Added patch to use nspr rather than mozilla-nspr when doing pkg-config tests
  (Patch5: evolution-data-server-1.3.5-nspr_fix.patch)

* Mon Jul 25 2005 David Malcolm <dmalcolm@redhat.com> - 1.3.5-1
- 1.3.5
- Split eds_major (was 1.2) into eds_base_version (1.4) and eds_api_version
  (1.2) to correspond to BASE_VERSION and API_VERSION in configure.in; updated
  rest of specfile accordingly.
- Removed upstreamed patch: 
  evolution-data-server-1.2.0-cope-with-a-macro-called-read.patch

* Wed Jun 27 2005 David Malcolm <dmalcolm@redhat.com> - 1.2.2-4.fc5
- Added leak fixes for GNOME bug 309079 provided by Mark G. Adams

* Wed May 18 2005 David Malcolm <dmalcolm@redhat.com> - 1.2.2-3
- bumped libsoup requirement to 2.2.3; removed mozilla_build_version, using
  pkg-config instead for locating NSPRS and NSS headers/libraries (#158085)

* Mon Apr 11 2005 David Malcolm <dmalcolm@redhat.com> - 1.2.2-2
- added patch to calendar/libecal/e-cal.c to fix missing declaration of open_calendar

* Mon Apr 11 2005 David Malcolm <dmalcolm@redhat.com> - 1.2.2-1
- 1.2.2

* Thu Mar 17 2005 David Malcolm <dmalcolm@redhat.com> - 1.2.1-1
- 1.2.1

* Thu Mar 10 2005 David Malcolm <dmalcolm@redhat.com> - 1.2.0-3
- Removed explicit run-time spec-file requirement on mozilla.
  The Mozilla NSS API/ABI stabilised by version 1.7.3
  The libraries are always located in the libdir
  However, the headers are in /usr/include/mozilla-%{mozilla_build_version}
  and so they move each time the mozilla version changes.
  So we no longer have an explicit mozilla run-time requirement in the specfile; 
  a requirement on the appropriate NSS and NSPR .so files is automagically generated on build.
  We have an explicit, exact build-time version, so that we can find the headers (without
  invoking an RPM query from the spec file; to do so is considered bad practice)
- Introduced mozilla_build_version, to replace mozilla_version
- Set mozilla_build_version to 1.7.6 to reflect current state of tree

* Tue Mar  8 2005 David Malcolm <dmalcolm@redhat.com> - 1.2.0-2
- Added a patch to deal with glibc defining a macro called "read"

* Tue Mar  8 2005 David Malcolm <dmalcolm@redhat.com> - 1.2.0-1
- 1.2.0
- Removed patch for GCC 4 as this is now in upstream tarball

* Wed Mar  2 2005 Jeremy Katz <katzj@redhat.com> - 1.1.6-6
- rebuild to fix library linking silliness

* Tue Mar  1 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.6-5
- disabling gtk-doc on ia64 and s390x

* Tue Mar  1 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.6-4
- added macro use_gtk_doc; added missing BuildRequires on gtk-doc; enabled gtk-doc generation on all platforms (had been disabled on ia64)

* Tue Mar  1 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.6-3
- extended patch to deal with camel-groupwise-store-summary.c

* Tue Mar  1 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.6-2
- added patch to fix badly-scoped declaration of "namespace_clear" in camel-imap-store-summary.c

* Tue Mar  1 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.6-1
- 1.1.6

* Tue Feb  8 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.5-3
- rebuild

* Tue Feb  8 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.5-2
- forgot to fix sources

* Tue Feb  8 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.5-1
- 1.1.5

* Thu Jan 27 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.4.2-1
- Update from unstable 1.1.4.1 to unstable 1.1.1.4.2

* Wed Jan 26 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.4.1-3
- disable gtk-doc generation on ia64 for now

* Wed Jan 26 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.4.1-2
- Exclude ppc64 due to missing mozilla dependency

* Wed Jan 26 2005 David Malcolm <dmalcolm@redhat.com> - 1.1.4.1-1
- Update from 1.0.3 to 1.1.4.1
- Updated eds_major from 1.0 to 1.2; fixed translation search path.
- Removed 64-bit patch for calendar backend hash table; upstream now stores pointers to ECalBackendFactory, rather than GType
- Removed calendar optimisation patch for part of part of bug #141283 as this is now in the upstream tarball
- Added /usr/lib/evolution-data-server-%{eds_major} to cover the extensions, plus the camel code now in e-d-s, rather than evolution
- Added /usr/share/pixmaps/evolution-data-server-%{eds_major} to cover the category pixmaps
- Camel code from evolution is now in evolution-data-server:
  - Added camel-index-control and camel-lock-helper to packaged files
  - Added mozilla dependency code from the evolution package
  - Ditto for LDAP
  - Ditto for krb5
  - Ditto for NNTP support handling
  - Ditto for --enable-file-locking and --enable-dot-locking
- Added requirements on libbonobo, libgnomeui, gnome-vfs2, GConf2, libglade2
- Updated libsoup requirement from 2.2.1 to 2.2.2
- Enabled gtk-doc

* Wed Dec 15 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.3-2
- fixed packaging of translation files to reflect upstream change to GETTEXT_PACKAGE being evolution-data-server-1.0 rather than -1.5

* Wed Dec 15 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.3-1
- update from upstream 1.0.2 to 1.0.3:
  * Address Book
    - prevent e_book_commit_contact from crashing on multiple calls (Diego Gonzalez)
    - prevent file backend from crashing if uid of vcard is NULL (Diego Gonzalez)

  * Calendar
    #XB59904 - Speed up calendar queries (Rodrigo)
    #XB69624 - make changes in evo corresponding to soap schema changes  (Siva)
    - fix libical build for automake 1.9 (Rodney)
    - fix putenv usage for portability (Julio M. Merino Vidal)

  * Updated Translations:
    - sv (Christian Rose)

- Removed patches to fix build on x86_64 and calendar optimisation for XB59004 as these are in the upstream tarball

* Tue Dec  7 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.2-6
- Amortize writes to a local cache of a webcal calendar, fixing further aspect of #141283 (upstream bugzilla #70267), as posted to mailing list here:
http://lists.ximian.com/archives/public/evolution-patches/2004-December/008338.html
(The groupwise part of that patch did not cleanly apply, so I removed it).

* Thu Dec  2 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.2-5
- Added fix for #141283 (upstream bugzilla XB 59904), a backported calendar 
optimisation patch posted to upstream development mailing list here:
http://lists.ximian.com/archives/public/evolution-patches/2004-November/008139.html

* Wed Nov  3 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.2-4
- Added patch to fix usage of GINT_TO_POINTER/GPOINTER_TO_INT for calendar backend GType hash table, breaking on ia64  (#136914)

* Wed Oct 20 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.2-3
- added workaround for a backend leak that causes the "contacts" calendar 
backend to hold open an EBook for the local contacts (filed upstream at:
http://bugzilla.ximian.com/show_bug.cgi?id=68533 ); this was causing e-d-s to
never lose its last addressbook, and hence never quit.  We workaround this by
detecting this condition and exiting when it occurs, fixing bug #134851 and #134849.

* Tue Oct 12 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.2-2
- added patch to fix build on x86_64 (had multiple definitions of mutex code in libdb/dbinc.mutex.h)

* Tue Oct 12 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.2-1
- update from 1.0.1 to 1.0.2
- increased libsoup requirement to 2.2.1 to match configuration script

* Tue Sep 28 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.1-1
- update from 1.0.0 to 1.0.1
- removed patch that fixed warnings in calendar code (now in upstream tarball)

* Mon Sep 20 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.0-2
- fixed various warnings in the calendar code 
  (filed upstream here: http://bugzilla.ximian.com/show_bug.cgi?id=66383)

* Tue Sep 14 2004 David Malcolm <dmalcolm@redhat.com> - 1.0.0-1
- update from 0.0.99 to 1.0.0
- changed path in FTP source location from 0.0 to 1.0

* Tue Aug 31 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.99-1
- update from 0.0.98 to 0.0.99
- increased libsoup requirement to 2.2.0 to match configuration script

* Mon Aug 16 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.98-1
- updated tarball from 0.0.97 to 0.0.98; updated required libsoup version to 2.1.13

* Thu Aug  5 2004 Warren Togami <wtogami@redhat.com> - 0.0.97-2
- pkgconfig -devel Requires libbonobo-devel, libgnome-devel

* Wed Aug  4 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.97-1
- upgraded to 0.0.97; rewrote the package's description

* Mon Jul 26 2004 David Malcolm <dmalcolm@redhat.com>
- rebuilt

* Tue Jul 20 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.96-2
- added version numbers to the BuildRequires test for libsoup-devel and ORBit2-devel

* Tue Jul 20 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.96-1
- 0.0.96; libsoup required is now 2.1.12

* Thu Jul  8 2004 David Malcolm <dmalcolm@redhat.com>
- rebuilt

* Wed Jul  7 2004 David Malcolm <dmalcolm@redhat.com>
- rebuilt

* Tue Jul  6 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.95-1
- 0.0.95

* Thu Jun 17 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.94.1-1
- 0.0.94.1

* Mon Jun  7 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.94-2
- rebuilt

* Mon Jun  7 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.94-1
- 0.0.94

* Wed May 26 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.93-4
- added ORBit2 requirement

* Fri May 21 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.93-3
- rebuild again

* Fri May 21 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.93-2
- rebuilt

* Thu May 20 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.93-1
- 0.0.93; libsoup required is now 2.1.10

* Wed Apr 21 2004 David Malcolm <dmalcolm@redhat.com> - 0.0.92-1
- Update to 0.0.92; added a define and a requirement on the libsoup version

* Wed Mar 10 2004 Jeremy Katz <katzj@redhat.com> - 0.0.90-1
- 0.0.90

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Jan 26 2004 Jeremy Katz <katzj@redhat.com> - 0.0.6-1
- 0.0.6

* Wed Jan 21 2004 Jeremy Katz <katzj@redhat.com> - 0.0.5-2
- better fix by using system libtool

* Mon Jan 19 2004 Jeremy Katz <katzj@redhat.com> 0.0.5-1
- add some libdb linkage to make the build on x86_64 happy

* Wed Jan 14 2004 Jeremy Katz <katzj@redhat.com> 0.0.5-0
- update to 0.0.5

* Sat Jan  3 2004 Jeremy Katz <katzj@redhat.com> 0.0.4-0
- Initial build.
