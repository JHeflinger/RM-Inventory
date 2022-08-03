import base64
import requests


url = 'https://api.github.com/repos/JHeflinger/RM-Inventory/contents/activitylog.txt'
req = requests.get(url)
if req.status_code == requests.codes.ok:
    req = req.json()
    content = base64.b64decode(req['content'])
    print(content)
else:
    print('Content was not found.')