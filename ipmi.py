# The first part of the code handles the authentication and session management

import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time

from argparse import ArgumentParser
from getpass import getpass
import urllib.request
import urllib.parse
import urllib.error

parser = ArgumentParser()
hostip = parser.add_mutually_exclusive_group(required=False)
hostip.add_argument('-ip', '--hostip', action='store')
hostip.add_argument('HOST_IP', action='store', nargs='?')

username = parser.add_mutually_exclusive_group(required=False)
username.add_argument('-u', '--username', action='store')
username.add_argument(
    'USERNAME', 
    action='store', 
    help='Can also be provided interactively to hide from console history.', 
    nargs='?'
)

passwd = parser.add_mutually_exclusive_group(required=False)
passwd.add_argument('-pw', '--password', action='store')
passwd.add_argument(
    'PASSWORD', 
    action='store', 
    help='Can also be provided interactively to hide from console history.',
    nargs='?'
)

parser.add_argument(
    '-l', 
    '--launch', 
    action='store_true', 
    default=False, 
    help='Launch generated jviewer file with javaws after generating it.'
)

pargs = parser.parse_args()

ip = pargs.hostip or pargs.HOST_IP or input('Input host IP: ')
ipmi_user = pargs.username or pargs.USERNAME or getpass('Input username: ')
ipmi_pass = pargs.password or pargs.PASSWORD or getpass('Input password: ')

resp_search = re.compile(r"'(SESSION_COOKIE|STOKEN|SESSION_TOKEN)' : '(.+)'")

cookie_req = urllib.request.Request(
    data=urllib.parse.urlencode(
        {
            'WEBVAR_USERNAME': ipmi_user, 
            'WEBVAR_PASSWORD': ipmi_pass
        }
    ).encode('utf-8'),
    url='http://{}/rpc/WEBSES/create.asp'.format(ip)
)

try:
    cookie_raw = urllib.request.urlopen(cookie_req).read().decode('utf-8')
except urllib.error.URLError as e:
    print("Error: Could not connect to host. Please check the host IP and try again.")
    sys.exit()

cookie = resp_search.search(cookie_raw).groups()[1]

token_req = urllib.request.Request(
    headers={'Cookie': 'SessionCookie={}'.format(cookie)}, 
    url='http://{}/rpc/getsessiontoken.asp'.format(ip)
)
token_raw = urllib.request.urlopen(token_req).read().decode('utf-8')
token = resp_search.search(token_raw).groups()[1]

# The second part of the code generates the JViewer file and launches it

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
