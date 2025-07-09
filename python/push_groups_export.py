import requests

'''
this will grab the  list of okta to app "push groups" for the application in the URL below
okta don't document or make public this API, but it does exist as an internal one
(they are promising that a public API of some kind is coming in '25 https://ideas.okta.com/app/#/case/149281 )
as this is a hidden API, normal API auth tokens/oauth flows dont work
log into okta as an admin, record network activity while on the admin console
find an event in the logs and get from there the Cookie and X-Okta-XsrfToken
paste those in below as noted
these are both tied to your *current* admin session, if that expires
or is revoked by okta - usually because of session roaming etc,
then the token and cookie here wont work
'''

'''
this is pretty simple script with a singular purpose
it only reads from okta so can't cause much damage
it includes pretty much no error handling
the most likely error is authorization - start there
'''

# set starting URL - change the app ID if you need, this is google workspace right now
domain = 'example'
app_id = '00-app-id-00'
url = f"https://{domain}-admin.okta.com/api/internal/instance/{app_id}/grouppush"

# get the cookie and token from your browsing session
# token is the value for header "X-Okta-XsrfToken"
cookie = 'COOKIE_HERE'
token = 'TOKEN_HERE'


# create the CSV headers
# the csv just saves to whatever directory this is running from, its not fancy with any path imported
with open('push_groups.csv', 'w') as f:
    f.write('"status","okta_group_id","okta_group_name","okta_source_app","app_group_name"\n')

# start a loop with the url input up top
while url:
    # these headers are intercepted from the admin console browsing sessions as mentioned before
    # make sure the cookie and token are good!
    headers = {
        'host': 'something-admin.okta.com',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Okta-XsrfToken': token,
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-ch-ua-platform-version': '"14.6.1"',
        'Cookie': cookie
    }
    # get the json body from the response
    response = requests.get(url, headers=headers)
    data = response.json()

    # write the key values to the csv that we want in the 'mappings' array
    with open('push_groups.csv', 'a') as f:
        for mapping in data['mappings']:
            line = f'"{mapping["status"]}","{mapping["sourceUserGroupId"]}","{mapping["sourceGroupName"]}","{mapping["sourceGroupAppName"]}","{mapping["targetGroupName"]}"\n'
            f.write(line)

    # Get next page URL if its there from the key "nextMappingsPageUrl"
    # this is different to okta's usual pagination in the public APis
    url = data.get('nextMappingsPageUrl')
'''
show done on screen
because i like a little on screen feedback
to tell me at a glance when things complete
'''
print("done")
