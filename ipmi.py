# The first part of the code handles the authentication and session management

import sys
import re
from urllib import request
from urllib.parse import urlencode
from getpass import getpass

if sys.version[0] == '2':
    input = raw_input

ip = input('Input host IP: ')
ipmi_user = input('Input username: ')
ipmi_pass = getpass('Input password: ')

# Regex pattern to find session data
resp_search = re.compile(r"'(SESSION_COOKIE|STOKEN|SESSION_TOKEN)' : '(.+)'")

# URLs to get session cookie and session token
cookie_url = 'http://{}/rpc/WEBSES/create.asp'.format(ip)
token_url = 'http://{}/rpc/getsessiontoken.asp'.format(ip)

# Request to create session cookie
cookie_req = request.Request(
    data=urlencode(
        {
            'WEBVAR_USERNAME': ipmi_user, 
            'WEBVAR_PASSWORD': ipmi_pass
        }
    ).encode('utf-8'),
    url='http://{}/rpc/WEBSES/create.asp'.format(ip)
)

try:
    cookie_raw = urllib.request.urlopen(cookie_req).read().decode('utf-8')
except error.URLError as e:
    print("Error connecting to server: ", e.reason)
    sys.exit(1)

# Find session cookie in the response
cookie_match = resp_search.search(cookie_raw)

if cookie_match is None:
    print('Could not find session cookie.')
    sys.exit(1)

cookie = cookie_match.groups()[1]

# Request to create session token
token_req = urllib.request.Request(
    headers={'Cookie': 'SessionCookie={}'.format(cookie)}, 
    url=token_url
)

try:
    token_raw = urllib.request.urlopen(token_req).read().decode('utf-8')
except error.URLError as e:
    print("Error connecting to server: ", e.reason)
    sys.exit(1)

# Find session token in the response
token_match = resp_search.search(token_raw)

if token_match is None:
    print('Could not find session token.')
    sys.exit(1)

token = token_match.groups()[1]

# The second part of the code generates the JViewer file and launches it

import os
import subprocess
import tempfile
import shutil
import time

jnlp_template = """\
<?xml version="1.0" encoding="UTF-8"?>
<jnlp spec="1.0+" codebase="https://{ip}/Java">
    <information>
        <title>JViewer</title>
        <vendor>American Megatrends, Inc.</vendor>
        <description kind="one-line">
            JViewer Console Redirection Application
        </description>
        <description kind="tooltip">
            JViewer Console Redirection Application
        </description>
        <description kind="short">
            JViewer enables a user to view the video display 
            of managed server via KVM. It also enables the 
            user to redirect his local keyboard, mouse for 
            managing the server remotely.
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
    <resources os="Linux" arch="x86_64">
        <j2se version="1.5+"/>
        <nativelib href="release/Linux_x86_64.jar"/>
    </resources>
    <resources os="Linux" arch="amd64">
        <j2se version="1.5+"/>
        <nativelib href="release/Linux_x86_64.jar"/>
    </resources>
    <application-desc>
        <argument>{ip}</argument>
        <argument>7578</argument>
        <argument>{token}</argument>
        <argument>{cookie}</argument>
    </application-desc>
</jnlp>
""".format(ip=ip, token=token, cookie=cookie)

with open('jviewer.jnlp', 'w') as fh:
    fh.write(jnlp_template)

print(f"jviewer.jnlp file created successfully! Location: {os.getcwd()}")

# Ask the user if they want to open the file
open_file = input("Do you want to open the jviewer.jnlp file? (y/n)")

# If the user enters 'y', open jviewer.jnlp
if open_file.lower() == "y":
    os.system("javaws jviewer.jnlp")
