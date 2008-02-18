#Module-Specific definitions
%define mod_name mod_protection
%define mod_conf 26_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	0.0.2
Release:	%mkrel 5
Group:		System/Servers
License:	GPL
URL:		http://www.twlc.net/
Source0:	%{mod_name}2-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		mod_protection2-0.0.2-register.patch
Patch1:		mod_protection2-0.0.2-apache220.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_protection is an apache module that integrates the basic
function of an IDS (Intrusion Detection System) and a firewall.

When a malicious client sends a request that matches a rule, the
administrator will be warned and the client gets an error message.

%prep

%setup -q -n %{mod_name}2-%{version}
%patch0 -p0
%patch1 -p0

# cleanup
rm -r *.*a *.*o*
rm -rf .libs

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%{_sbindir}/apxs -c mod_protection.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

install -d %{buildroot}%{_sysconfdir}/httpd//conf
install -m640 mod_protection.rules %{buildroot}%{_sysconfdir}/httpd//conf/

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc Changes INSTALL README THANX TODO USAGE
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/mod_protection.rules
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*


