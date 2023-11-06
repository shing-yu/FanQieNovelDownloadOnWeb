import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree

url = 'http://192.168.2.18:5244/dav/'
username = 'admin'
password = 'gsw091005'

headers = {
    "Depth": "1",
}
auth = HTTPBasicAuth(username, password)

# Make a PROPFIND request to list the files and directories
response = requests.request("PROPFIND", url, headers=headers, auth=auth)

if response.status_code == 207:
    # Parse the XML response to extract file and directory names
    namespaces = {'d': 'DAV:'}
    xml = ElementTree.fromstring(response.content)

for item in xml.findall(".//d:href", namespaces):
    href = item.text
    # Remove the server URL to get the file/directory name
    file_name = href.replace(url, "")
    print(file_name)
else:
    print(f"Failed to list files. Status code: {response.status_code}")
