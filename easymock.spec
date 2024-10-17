%{?_javapackages_macros:%_javapackages_macros}
Name:           easymock
Version:        3.2
Release:        1.1%{?dist}
Summary:        Easy mock objects
License:        ASL 2.0
URL:            https://www.easymock.org

Source0:        https://github.com/easymock/easymock/archive/easymock-%{version}.tar.gz

Patch5:         %{name}-remove-android-support.patch

BuildArch:      noarch

BuildRequires:  maven-local
BuildRequires:  mvn(com.keyboardsamurais.maven:maven-timestamp-plugin)
BuildRequires:  mvn(com.mycila.maven-license-plugin:maven-license-plugin)
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(net.sf.cglib:cglib)
BuildRequires:  mvn(org.apache.maven.plugins:maven-compiler-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-jar-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-remote-resources-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-surefire-plugin)
BuildRequires:  mvn(org.objenesis:objenesis)
BuildRequires:  mvn(org.codehaus.mojo:build-helper-maven-plugin)

Obsoletes:      %{name}3 < %{version}-%{release}
Provides:       %{name}3 = %{version}-%{release}


%description
EasyMock provides Mock Objects for interfaces in JUnit tests by generating
them on the fly using Java's proxy mechanism. Due to EasyMock's unique style
of recording expectations, most refactorings will not affect the Mock Objects.
So EasyMock is a perfect fit for Test-Driven Development.


%package javadoc
Summary:        Javadoc for %{name}

%description javadoc
Javadoc for %{name}.


%prep
# Unpack the sources:
%setup -q -n easymock-easymock-%{version}

find . -name "*.zip" -delete

# remove android support
%patch5 -p1
%pom_xpath_remove "pom:profile[pom:id[text()='android']]"
%pom_remove_dep :dexmaker easymock

# fix cglib aId and gId
%pom_remove_dep :cglib-nodep easymock
%pom_add_dep net.sf.cglib:cglib easymock

# remove some warning caused by unavailable plugin
%pom_remove_plugin com.atlassian.maven.plugins:maven-clover2-plugin
%pom_remove_plugin org.codehaus.mojo:versions-maven-plugin
%pom_xpath_remove pom:profiles easymock-classextension

%pom_disable_module easymock-integration

# For compatibility reasons
%mvn_file ":easymock{*}" easymock@1 easymock3@1


%build
%mvn_build

%install
%mvn_install


%files -f .mfiles
%doc easymock/LICENSE.txt

%files javadoc -f .mfiles-javadoc
%doc easymock/LICENSE.txt


%changelog
* Fri Aug 30 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:3.2-1
- Update to upstream version 3.2

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2-21
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Feb 18 2013 Tomas Radej <tradej@redhat.com> - 0:1.2-20
- Fixed sources (bz #905973)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Nov 27 2012 Tomas Radej <tradej@redhat.com> - 0:1.2-18
- Removed ownership of _mavenpomdir

* Thu Aug 16 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:1.2-17
- Add LICENSE file
- Remove rpm bug workaround
- Update to current packaging guidelines

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Feb 21 2012 Tomas Radej <tradej@redhat.com> - 0:1.2-15
- Removed test

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Nov 26 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0:1.2-12
- Fix pom filename (Resolves rhbz#655795)
- Remove clean section and buildroot declaration
- Remove versioned jars and pom files

* Thu Aug 20 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.2-11
- Bump release for rebuild.

* Thu Aug 20 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.2-10
- Disable tests.

* Mon May 18 2009 Fernando Nasser <fnasser@redhat.com> 0:1.2-9
- Update instructions for obtaining source tar ball

* Mon May 04 2009 Yong Yang <yyang@redhat.com> 0:1.2-8
- Rebuild with maven2-2.0.8 built in non-bootstrap mode

* Wed Mar 18 2009 Yong Yang <yyang@redhat.com>  0:1.2-7
- merge from JPP-6
- rebuild with new maven2 2.0.8 built in bootstrap mode

* Mon Feb 02 2009 David Walluck <dwalluck@redhat.com> 0:1.2-6
- fix component-info.xml

* Mon Feb 02 2009 David Walluck <dwalluck@redhat.com> 0:1.2-5
- remove unneeded maven flag

* Mon Feb 02 2009 David Walluck <dwalluck@redhat.com> 0:1.2-4
- add repolib

* Fri Jan 30 2009 Will Tatam <will.tatam@red61.com> 1.2-3.jpp5
- Inital JPP-5 Build

* Fri Jan 09 2009 Yong Yang <yyang@redhat.com> 1.2-2jpp.1
- Imported from dbhole's maven 2.0.8 packages, initial building on jpp6

* Fri Apr 11 2008 Deepak Bhole <dbhole@redhat.com> 1.2-1jpp.1
- Import from JPackage
- Add pom file

* Fri Feb 24 2006 Ralph Apel <r.apel at r-apel.de> - 0:1.2-1jpp
- Update to 1.2 keeping only java 1.4 requirement

* Fri Feb 24 2006 Ralph Apel <r.apel at r-apel.de> - 0:1.1-3jpp
- drop java-1.3.1 requirement

* Mon Oct 04 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.1-2jpp
- Fixed Url, Summary, Description and License

* Mon Oct 04 2004 Ralph Apel <r.apel at r-apel.de> - 0:1.1-1jpp
- First JPackage release
