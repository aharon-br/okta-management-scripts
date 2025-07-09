import os
from libs.functions import okta_api_call, get_okta_token_read_only

'''
this gets a list of all devices in okta
and also gets the registered user if there is one
'''

domain = "example"

base_url = f"https://{domain}.okta.com/api/v1/devices"
    
scopes = "okta.devices.read"
bearer_token = get_okta_token_read_only(scopes)
token = f"Bearer {bearer_token}"

# create the csv in the same directory called "devices_list.csv"
# add the column headers
with open(os.path.expanduser("~/Downloads/devices_list.csv"), 'w') as file:
    file.write(
           '"device ID","display name","platform","registered",'
           '"managed","user id","user email"\n'
           )

'''
url for the query with expand=user specified
this is kept at 50 as anything larger gets a lot of time-outs.
if you still get time-outs at 50, reduce to 20
which is oktas recommended number but also insanely low
'''
url = base_url + "?limit=50&expand=user"

with open(os.path.expanduser("~/Downloads/devices_list.csv"), 'a') as file:

    devices_list = okta_api_call(url, token, method='get',)
    # for each device object in the list
    for device in devices_list:
        # if the _embedded.users object is present
        # then output a new line to the CSV with that info present
        if device["_embedded"]["users"]:
            user_data = device["_embedded"]["users"][0]["user"]
            new_line = (
                f'"{device["id"]}","{device["profile"]["displayName"]}",'
                f'"{device["profile"]["platform"]}",'
                f'"{device["profile"]["registered"]}",'
                f'"{device["_embedded"]["users"][0]["managementStatus"]}",'
                f'"{user_data["id"]}",'
                f'"{user_data["profile"]["login"]}"\n'
                )

            file.write(new_line)
        # but if the _embedded.users object is missing
        # output the new line, but with those columns empty
        else:
            new_line = (
                f'"{device["id"]}","{device["profile"]["displayName"]}",'
                f'"{device["profile"]["platform"]}",'
                f'"{device["profile"]["registered"]}",'
                f'"",'  # Empty strings
                f'"",'
                f'""\n'
                )
            file.write(new_line)
    print("File in Downloads")
