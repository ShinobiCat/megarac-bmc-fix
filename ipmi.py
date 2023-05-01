#! /usr/bin/env python

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

if sys.version[0] == '2':
    from urllib import urlencode
    from urllib2 import urlopen, Request
else:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request


parser = ArgumentParser()
parser.add_argument(
    '-l', 
    '--launch', 
    action='store_true', 
    default=False, 
    help='Launch generated jviewer file with javaws after generating it.'
)

pargs = parser.parse_args()

try:
    ip = input('Enter host IP: ')
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
        raise ValueError('Invalid IP address')
    ipmi_user = input('Enter username: ')
    if not ipmi_user:
        raise ValueError('Username cannot be empty')
    ipmi_pass = getpass('Enter password: ')
    if not ipmi_pass:
        raise ValueError('Password cannot be empty')

    resp_search = re.compile(r"'(SESSION_COOKIE|STOKEN|SESSION_TOKEN)' : '(.+)'")

    cookie_req = Request(
        data=urlencode(
            {
                'WEBVAR_USERNAME': ipmi_user, 
                'WEBVAR_PASSWORD': ipmi_pass
            }
        ).encode('utf-8'),
        url='http://{}/rpc/WEBSES/create.asp'.format(ip)
    )
    cookie_raw = urlopen(cookie_req).read().decode('utf-8')
    cookie = resp_search.search(cookie_raw).groups()[1]

    token_req = Request(
        headers={'Cookie': 'SessionCookie={}'.format(cookie)}, 
        url='http://{}/rpc/getsessiontoken.asp'.format(ip)
    )
    token_raw = urlopen(token_req).read().decode('utf-8')
    token = resp_search.search(token_raw).groups()[1]

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
        </

