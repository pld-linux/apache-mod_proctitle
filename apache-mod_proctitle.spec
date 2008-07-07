%define		mod_name	proctitle
%define 	apxs		/usr/sbin/apxs
Summary:	Apache module: set process name to currently serverd virtual host
Name:		apache-mod_%{mod_name}
Version:	0.1
Release:	0.20080707
License:	Apache v2.0
Group:		Networking/Daemons
Source0:	mod_proctitle.c
# Source0-md5:	e4974a4f7c7c7848eca8748c91c24062
BuildRequires:	%{apxs}
BuildRequires:	apache-devel >= 2.0
BuildRequires:	rpmbuild(macros) >= 1.268
Requires:	apache(modules-api) = %apache_modules_api
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)
%define		_pkglogdir	%(%{apxs} -q PREFIX 2>/dev/null)/logs

%description
mod_proctitle is an experimental module for Apache httpd 2.x which
changes process name to currently served virtual host.

%prep
%setup -q -c -T
install %{SOURCE0} .

%build
%{apxs} -c mod_%{mod_name}.c -o mod_%{mod_name}.la

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}/httpd.conf,/var/log/httpd}
install .libs/mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}

cat > $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf/90_mod_%{mod_name}.conf << 'EOF'
LoadModule %{mod_name}_module modules/mod_%{mod_name}.so
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
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*.so
