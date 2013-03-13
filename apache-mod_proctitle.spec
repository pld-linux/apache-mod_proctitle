%define		mod_name	proctitle
%define 	apxs		/usr/sbin/apxs
Summary:	Apache module: set process name to currently serverd virtual host
Name:		apache-mod_%{mod_name}
Version:	0.4
Release:	2
License:	Apache v2.0
Group:		Networking/Daemons/HTTP
Source0:	https://github.com/stass/mod_proctitle/archive/0.4.tar.gz
# Source0-md5:	83043432da02f0ebf6de4badbe404dcd
Patch0:		setproctitle.patch
URL:		https://github.com/stass/mod_proctitle
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.0
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	setproctitle-devel
Requires:	apache(modules-api) = %apache_modules_api
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)/conf.d

%description
mod_proctitle is an experimental module for Apache httpd 2.x which
changes process name to currently served virtual host.

%prep
%setup -q -n mod_%{mod_name}-%{version}
%patch0 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoheader}
%{__autoconf}
%{__automake}

CPPFLAGS="%{rpmcppflags} -D__unused='__attribute__ ((__unused__))'" \
APXS="%{apxs}" \
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cat > $RPM_BUILD_ROOT%{_sysconfdir}/90_mod_%{mod_name}.conf << 'EOF'
LoadModule %{mod_name}_module modules/mod_%{mod_name}.so
ProctitileEnable On
# ProctitleUriSep ::
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%service -q httpd restart

%postun
if [ "$1" = "0" ]; then
	%service -q httpd restart
fi

%files
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/mod_proctitle.so
