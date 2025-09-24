Name:           ailt
Version:        0.1.0
Release:        1%{?dist}
Summary:        AI Linux Terminal - natural language shell

License:        MIT
URL:            https://yourwebsite.com/ailt
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires:       python3-requests
Requires:       python3-rich
Requires:       python3-distro
Requires:       ollama

%description
AILT (AI Linux Terminal) is a command-line tool that lets you run
Linux commands by describing them in natural language.

%prep
%autosetup -n %{name}-%{version}

%build
%py3_build

%install
rm -rf %{buildroot}
%py3_install

%files
%license LICENSE
%doc README.md FUNDING.md
%{python3_sitelib}/ailt*
%{_bindir}/ailt

%changelog
* Mon Sep 23 2025 Luka Beslic <devluka.public@gmail.com> - 0.1.0-1
- Initial Fedora RPM release of AILT
