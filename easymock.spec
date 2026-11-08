Name:		easymock
Version:	5.7.0
Release:	1
Summary:	Mock objects for Java interfaces and classes
Group:		Development/Java
License:	Apache-2.0
URL:		https://easymock.org
Source0:	https://codeload.github.com/easymock/easymock/tar.gz/refs/tags/easymock-%{version}#/easymock-%{version}.tar.gz
BuildArch:	noarch
# The 3.2 package was also installable as easymock3.
Obsoletes:	easymock3 < %{version}-%{release}
Provides:	easymock3 = %{version}-%{release}
BuildRequires:	java-current-devel
BuildRequires:	python
BuildRequires:	sysjar
BuildRequires:	mvn(net.bytebuddy:byte-buddy)
BuildRequires:	mvn(org.objenesis:objenesis)
BuildRequires:	mvn(org.ow2.asm:asm)
BuildRequires:	mvn(org.ow2.asm:asm-commons)
BuildRequires:	mvn(junit:junit)

%description
EasyMock creates mock objects for Java interfaces and classes. Class
mocks are generated with the system copy of Byte Buddy. The JUnit 4
rule and runner are included. The JUnit Jupiter extension, the TestNG
listener, and Android class mocking are not.

%prep
%setup -q -n easymock-easymock-%{version}
find . -name '*.class' -delete
find . -name '*.jar' -delete
if find . \( -name '*.class' -o -name '*.jar' \) | grep -q .; then
	echo "prebuilt bytecode remains" >&2
	exit 1
fi
rm -f core/src/main/java/org/easymock/EasyMockExtension.java \
	core/src/main/java/org/easymock/EasyMockListener.java
python - << 'PY'
from pathlib import Path
path = Path("core/src/main/java/org/easymock/internal/AndroidClassProxyFactory.java")
text = path.read_text(encoding="utf-8")
if "org.droidparts.dexmaker" not in text:
    raise SystemExit("android factory no longer imports dexmaker")
path.write_text(r'''
/*
 * Copyright 2001-2026 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.easymock.internal;

import org.easymock.ConstructorArgs;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;

/**
 * Android class mocking needs dexmaker, which is not part of this system.
 * AndroidSupport.isAndroid() stays false without dalvik, so a normal JVM
 * never calls this factory.
 */
public final class AndroidClassProxyFactory implements IProxyFactory {
    public <T> T createProxy(Class<T> toMock, InvocationHandler handler,
            Method[] mockedMethods, ConstructorArgs constructorArgs) {
        throw new UnsupportedOperationException("Android class mocking is not available");
    }

    public InvocationHandler getInvocationHandler(Object mock) {
        throw new UnsupportedOperationException("Android class mocking is not available");
    }
}
'''.strip() + "\n", encoding="utf-8")
PY

%build
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
CP=/usr/share/java/byte-buddy.jar:/usr/share/java/objenesis.jar:/usr/share/java/junit.jar
mkdir -p build/classes
find core/src/main/java -name '*.java' | sort > build/sources.list
python - << 'PY'
from pathlib import Path
lines = Path("build/sources.list").read_text().splitlines()
if len(lines) != 91:
    raise SystemExit("source count " + str(len(lines)))
if any(name.endswith("EasyMockExtension.java") or name.endswith("EasyMockListener.java") for name in lines):
    raise SystemExit("excluded source still listed")
PY
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 -cp "$CP" \
	-d build/classes @build/sources.list
python - << 'PY'
import os
from pathlib import Path
root = Path("build/classes")
count = 0
for path in root.rglob("*.class"):
    data = path.read_bytes()
    major = int.from_bytes(data[6:8], "big")
    if major != 52:
        raise SystemExit(str(path) + " has major " + str(major))
    count += 1
if count != 104:
    raise SystemExit("class count " + str(count))
PY
cat > build/manifest.mf << 'EOF'
Manifest-Version: 1.0
Implementation-Title: org.easymock
Implementation-Version: %{version}
Specification-Title: EasyMock
Specification-Version: %{version}
Automatic-Module-Name: org.easymock

EOF
"$JAVA_HOME/bin/jar" --create --manifest build/manifest.mf \
	--file build/easymock.jar -C build/classes .
cat > build/easymock.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.easymock</groupId>
  <artifactId>easymock</artifactId>
  <version>%{version}</version>
  <name>EasyMock</name>
  <description>Mock objects for interfaces and classes, built against the system Byte Buddy.</description>
  <url>https://easymock.org</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>net.bytebuddy</groupId>
      <artifactId>byte-buddy</artifactId>
      <version>1.18.17</version>
    </dependency>
    <dependency>
      <groupId>org.ow2.asm</groupId>
      <artifactId>asm</artifactId>
      <version>9.11.1</version>
      <scope>runtime</scope>
    </dependency>
    <dependency>
      <groupId>org.objenesis</groupId>
      <artifactId>objenesis</artifactId>
      <version>3.6</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact build/easymock.pom:build/easymock.jar \
	--file-name easymock \
	--filelist .mfiles

%check
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
"$JAVA_HOME/bin/jar" tf build/easymock.jar > build/jar-list.txt
for class in \
	org/easymock/EasyMock.class \
	org/easymock/EasyMockRule.class \
	org/easymock/EasyMockRunner.class \
	org/easymock/internal/EasyMockStatement.class \
	org/easymock/internal/AndroidClassProxyFactory.class
do
	if ! grep -F -x -q "$class" build/jar-list.txt; then
		echo "missing $class" >&2
		exit 1
	fi
done
if grep -F -e EasyMockExtension -e EasyMockListener -e droidparts -e dexmaker -e module-info.class build/jar-list.txt; then
	echo "jar contains an excluded class" >&2
	exit 1
fi
"$JAVA_HOME/bin/jar" --describe-module --file build/easymock.jar > build/module.txt
if ! grep -F -q 'org.easymock automatic' build/module.txt; then
	echo "automatic module name" >&2
	exit 1
fi
mkdir -p build/probe
cat > build/Probe.java << 'EOF'
import static org.easymock.EasyMock.expect;
import static org.easymock.EasyMock.mock;
import static org.easymock.EasyMock.replay;
import static org.easymock.EasyMock.verify;

public class Probe {
	public interface Adder {
		int add(int a, int b);
	}

	public static class Box {
		public int value() {
			return 1;
		}
	}

	public static void main(String[] args) {
		Adder adder = mock(Adder.class);
		expect(adder.add(1, 2)).andReturn(3);
		replay(adder);
		if (adder.add(1, 2) != 3) {
			throw new RuntimeException("interface mock");
		}
		verify(adder);

		Box box = mock(Box.class);
		expect(box.value()).andReturn(4);
		replay(box);
		if (box.value() != 4) {
			throw new RuntimeException("class mock");
		}
		verify(box);
		System.out.println("probe ok");
	}
}
EOF
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 \
	-cp build/easymock.jar -d build/probe build/Probe.java
"$JAVA_HOME/bin/java" --enable-native-access=ALL-UNNAMED \
	-cp "build/probe:build/easymock.jar:/usr/share/java/byte-buddy.jar:/usr/share/java/objenesis.jar:/usr/share/java/asm.jar:/usr/share/java/asm-commons.jar" \
	Probe > build/probe.out
if ! grep -F -x -q 'probe ok' build/probe.out; then
	echo "probe failed" >&2
	exit 1
fi

%files -f .mfiles
%license core/LICENSE.txt
%doc README.md ReleaseNotes.md
