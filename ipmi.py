#!/usr/bin/env python3

import os
import sys
import urllib.request
import urllib.parse
import re
from getpass import getpass

IP = input("IP Address: ")
IPMI_USER = input("Username: ")
IPMI_PASS = getpass("Password: ")

OUTFILE = "/tmp/" + IP + "_jviewer.jnlp"

COOKIE_REQ = urllib.request.Request(
    "http://" + IP + "/rpc/WEBSES/create.asp",
    urllib.parse.urlencode({
        "WEBVAR_USERNAME": IPMI_USER,
        "WEBVAR_PASSWORD": IPMI_PASS
    }).encode()
)

try:
    COOKIE_RAW = urllib.request.urlopen(COOKIE_REQ).read().decode('utf-8')
    COOKIE_SEARCH = re.search(r"\'SESSION\_COOKIE\'\s\:\s\'(.*?)\'", COOKIE_RAW, re.MULTILINE|re.DOTALL)
    COOKIE = COOKIE_SEARCH.group(1)
except (urllib.error.URLError, AttributeError):
    print("Failed to extract login cookie")
    sys.exit(1)

TOKEN_REQ = urllib.request.Request(
    "http://" + IP + "/rpc/getsessiontoken.asp",
    headers={"Cookie": "SessionCookie=" + COOKIE}
)

try:
    TOKEN_RAW = urllib.request.urlopen(TOKEN_REQ).read().decode('utf-8')
    TOKEN_SEARCH = re.search(r"\'STOKEN\'\s\:\s\'(.*?)\'", TOKEN_RAW, re.MULTILINE|re.DOTALL)
    TOKEN = TOKEN_SEARCH.group(1)
except (urllib.error.URLError, AttributeError):
    print("Failed to extract session token")
    sys.exit(1)

with open(OUTFILE, 'w') as f:
    f.write(f"""\
<?xml version="1.0" encoding="UTF-8"?>
<jnlp spec="1.0+" codebase="https://{IP}/Java">
	<information>
		<title>JViewer</title>
		<vendor>American Megatrends, Inc.</vendor>
		<description kind="one-line">JViewer Console Redirection Application</description>
		<description kind="tooltip">JViewer Console Redirection Application</description>
		<description kind="short">
			JViewer enables a user to view the video display of managed server via KVM.
			It also enables the user to redirect his local keyboard, mouse for managing the server remotely.
		</description>
	</information>
	<security>
		<all-permissions/>
	</security>
	<resources>
		<j2se version="1.5+"/>
		<jar href="release/JViewer.jar"/>
	</resources>
	<resources os="Windows" arch="amd64">
		<j2se version="1.5+"/>
		<nativelib href="release/Win64.jar"/>
	</resources>
	<resources os="Windows" arch="x86">
		<j2se version="1.5+"/>
		<nativelib href="release/Win32.jar"/>
	</resources>
	<resources os="Linux" arch="x86">
		<j2se version="1.5+"/>
		<nativelib href="release/Linux_x86_32.jar"/>
	</resources>
<resources os="Linux" arch="i386">
    <j2se version="1.5+"/>
    <nativelib href="release/Linux_x86_.jar"/>
</resources>
<resources os="Linux" arch="x86_64">
    <j2se version="1.5+"/>
    <nativelib href="release/Linux_x86_64.jar"/>
</resources>
<application-desc>
    <argument>${IP}</argument>
    <argument>7578</argument>
    <argument>${TOKEN}</argument>
    <argument>${COOKIE}</argument>
</application-desc>
</jnlp>
""")

try:
    # Launch the JViewer application using javaws
    cmd = f"javaws -nosecurity -jnlp {OUTFILE} >/dev/null & disown && sleep 1 && rm -f {OUTFILE}"
    os.system(cmd)
except OSError as e:
    print(f"Error launching JViewer application: {e}")
    sys.exit(1)
