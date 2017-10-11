%global pyname smclip
%global summary Simple Multi Command Line Parser
%if 0%{?fedora}
%global with_python3 1
%else
%global with_python3 0
%endif

Name:           python-%{pyname}
Version:        0.3.0
Release:        1%{?dist}
Summary:        %{summary}

Group:          Development/Libraries
License:        LGPL
URL:            https://pypi.python.org/pypi/smclip
Source0:        https://files.pythonhosted.org/packages/source/s/%{pyname}/%{pyname}-%{version}.tar.gz

BuildArch:      noarch

%if 0%{?fedora}
BuildRequires:  python2-devel
%else
# RHEL/CentOS (requires EPEL)
BuildRequires:  python-devel
BuildRequires:  python2-rpm-macros
%endif

BuildRequires:  pytest
BuildRequires:  python2-mock
%if 0%{?with_python3}
BuildRequires:  python3-devel
BuildRequires:  python3-pytest
%endif

%description
An python module which provides a simple framework for parsing
multi command line arguments.

%package -n python2-%{pyname}
Summary:        %{summary}
%{?python_provide:%python_provide python2-%{pyname}}

%description -n python2-%{pyname}
An python module which provides a simple framework for parsing
multi command line arguments.

%if 0%{?with_python3}
%package -n python3-%{pyname}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pyname}}

%description -n python3-%{pyname}
An python module which provides a simple framework for parsing
multi command line arguments.
%endif

%prep
%autosetup -n %{pyname}-%{version}

%build
%py2_build
%if 0%{?with_python3}
%py3_build
%endif


%install
%py2_install
%if 0%{?with_python3}
%py3_install
%endif

%check
%{__python2} -m pytest
%if 0%{?with_python3}
%{__python3} -m pytest
%endif

# Note that there is no %%files section for the unversioned python module if we are building for several python runtimes
%files -n python2-%{pyname}
%license LICENSE
%doc README.rst
%{python2_sitelib}/*

%if 0%{?with_python3}
%files -n python3-%{pyname}
%license LICENSE
%doc README.rst
%{python3_sitelib}/*
%endif

%changelog
* Wed Oct 11 2017 Viliam Krizan <vkrizan AT redhat.com> 0.3.0-1
- improved doc string parsing for help
- possible subcommands for defined arguments for bash completion

* Mon Mar 06 2017 Viliam Krizan <vkrizan AT redhat.com> 0.2.2-2
- Support build for EL7

* Wed Oct 26 2016 Viliam Krizan <vkrizan AT redhat.com> 0.2.1-1
- Initial packaging.
