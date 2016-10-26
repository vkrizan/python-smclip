%global pyname smclip
%global summary Simple Multi Command Line Parser

Name:           python-%{pyname}
Version:        0.2.2
Release:        1%{?dist}
Summary:        %{summary}

Group:          Development/Libraries
License:        LGPL
URL:            https://pypi.python.org/pypi/smclip
Source0:        https://files.pythonhosted.org/packages/source/s/%{pyname}/%{pyname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python3-devel
BuildRequires:  pytest
BuildRequires:  python3-pytest
BuildRequires:  python-mock

%description
An python module which provides a simple framework for parsing
multi command line arguments.

%package -n python2-%{pyname}
Summary:        %{summary}
%{?python_provide:%python_provide python2-%{pyname}}

%description -n python2-%{pyname}
An python module which provides a simple framework for parsing
multi command line arguments.


%package -n python3-%{pyname}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pyname}}

%description -n python3-%{pyname}
An python module which provides a simple framework for parsing
multi command line arguments.


%prep
%autosetup -n %{pyname}-%{version}

%build
%py2_build
%py3_build

%install
%py2_install
%py3_install

%check
%{__python2} -m pytest
%{__python3} -m pytest

# Note that there is no %%files section for the unversioned python module if we are building for several python runtimes
%files -n python2-%{pyname}
%license LICENSE
%doc README.rst
%{python2_sitelib}/*

%files -n python3-%{pyname}
%license LICENSE
%doc README.rst
%{python3_sitelib}/*

%changelog
* Wed Oct 26 2016 Viliam Krizan <vkrizan AT redhat.com> 0.2.1
- Initial packaging.
