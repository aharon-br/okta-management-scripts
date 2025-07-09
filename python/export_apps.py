import json
import os
from libs.functions import okta_api_call, get_okta_token_read_only

'''
this exports every app into a json file
you can add in converting to a csv if you like
this is helpful just to make a copy of everything
'''

scopes = "okta.apps.read"
# get a token
token = get_okta_token_read_only(scopes)
bearer_token = f"Bearer {token}"

domain = 'example'
# set the URL to apps ULR
url = f"https://{domain}.okta.com/api/v1/apps"
method = 'get'

data = None

# use the api call function in the library to get the apps and paginate it
call_output = okta_api_call(url, bearer_token, method, data)

# save the json into user downloads folder
with open(os.path.expanduser("~/Downloads/apps-output.json"), 'w') as file:
    json.dump(call_output, file, indent=4)
