Name:           aureon-desktop
Version:        1.0.0
Release:        1%{?dist}
Summary:        AUREON OS Desktop Environment

License:        Proprietary / Open Core
URL:            https://aureon.dev
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  cmake >= 3.25
BuildRequires:  gcc-c++ >= 11
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
Requires:       pipewire NetworkManager

%description
AUREON OS provides a refined, unified glassmorphic desktop environment
with original AI assistant, smart dock, and universal search.

%prep
%setup -q

%build
%cmake
%cmake_build

%install
%cmake_install

%files
%{_bindir}/aureon-desktop
%{_datadir}/aureon/
