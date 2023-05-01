import urllib.parse
import urllib.request
import re
import getpass

# Prompt user for IP, username and password
ip = input("Enter IP address: ")
username = input("Enter username: ")
password = getpass.getpass("Enter password: ")

# Construct POST request to get session cookie
cookie_url = f"https://{ip}/rpc/WEBSES/create.asp"
cookie_data = urllib.parse.urlencode({"WEBVAR_USERNAME": username, "WEBVAR_PASSWORD": password}).encode("utf-8")
cookie_req = urllib.request.Request(
    url=url,
    data=urlencode({
        'WEBVAR_USERNAME': username,
        'WEBVAR_PASSWORD': password
    }).encode('ascii'),
    headers=headers,
    method='POST')


try:
    cookie_raw = urllib.request.urlopen(cookie_req).read().decode("utf-8")
except urllib.error.URLError as e:
    print(f"Failed to connect to {ip}: {e.reason}")
    exit()

# Extract token from response
resp_search = re.search(r"SESSION_COOKIE=\'(.*?)\';", cookie_raw)
if not resp_search:
    print("Failed to extract token from response")
    exit()

token_raw = resp_search.group(1)

# Validate token
if not re.match(r"[a-fA-F0-9]{32}", token_raw):
    print("Token is invalid")
    exit()

print("Token is valid")
