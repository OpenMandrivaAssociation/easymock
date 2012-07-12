# Copyright (c) 2000-2009, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

Name:           easymock
Version:        1.2
Release:        15
Summary:        Easy mock objects
Group:          Development/Java
License:        MIT
URL:            http://www.easymock.org/
# cvs -d:pserver:anonymous@easymock.cvs.sourceforge.net:/cvsroot/easymock login
# cvs -z3 -d:pserver:anonymous@easymock.cvs.sourceforge.net:/cvsroot/easymock export -r EasyMock1_2_Java1_3 easymock
# tar czf easymock-1.2-src.tar.gz easymock
Source0:        easymock-1.2-src.tar.gz
Source1:        http://repo1.maven.org/maven2/easymock/easymock/1.2_Java1.5/easymock-1.2_Java1.5.pom
Source2:        easymock-component-info.xml
Patch0:         easymock-1.2-build_xml.patch
Patch1:         %{name}-removed-test.patch
Patch2:         %{name}-removed-alltests.patch
Requires(post): jpackage-utils >= 1.7.2
Requires(postun): jpackage-utils >= 1.7.2
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  ant >= 0:1.6
BuildRequires:  ant-junit >= 0:1.6
BuildRequires:  junit >= 0:3.8.1
BuildRequires:  java-devel >= 0:1.5.0
BuildRequires:  java-rpmbuild
BuildArch:      noarch

%description
EasyMock provides Mock Objects for interfaces in JUnit tests by generating
them on the fly using Java's proxy mechanism. Due to EasyMock's unique style
of recording expectations, most refactorings will not affect the Mock Objects.
So EasyMock is a perfect fit for Test-Driven Development.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description    javadoc
Javadoc for %{name}.

%prep
%setup -q -n %{name}
%patch0 -p0
%patch1 -p1
%patch2 -p1
mkdir lib
pushd lib
ln -sf $(build-classpath junit) .
popd

# We no longer ship a 1.3/1.4 VM, Set it to generic javahome
rm easymockbuild.properties
echo "java\ 1.3=%{java}" >> easymockbuild.properties
echo "java\ 1.4=%{java}" >> easymockbuild.properties
echo "java\ 1.5=%{java}" >> easymockbuild.properties
echo "java\ compiler=%{javac}" >> easymockbuild.properties

%build
export OPT_JAR_LIST="ant/ant-junit junit"
export CLASSPATH=
%{ant} -Dbuild.sysclasspath=first

%install
unzip -qq %{name}%{version}_Java1.3.zip
install -dm 755 $RPM_BUILD_ROOT%{_javadir}

install -pm 644 %{name}%{version}_Java1.3/%{name}.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# javadoc
install -dm 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr %{name}%{version}_Java1.3/javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# pom
install -dm 755 $RPM_BUILD_ROOT%{_mavenpomdir}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}.pom
%add_to_maven_depmap easymock easymock %{version}_Java1.5 JPP easymock

%post
%update_maven_depmap

%postun
%update_maven_depmap

%pre javadoc
# workaround for rpm bug 646523 (can be removed in F-17)
[ $1 -gt 1 ] && [ -L %{_javadocdir}/%{name} ] && \
rm -rf $(readlink -f %{_javadocdir}/%{name}) %{_javadocdir}/%{name} || :

%files
%defattr(-,root,root,-)
%doc %{name}%{version}_Java1.3/{Documentation,License}.html
%{_mavenpomdir}*
%{_mavendepmapfragdir}/*
%{_javadir}/%{name}.jar

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}

