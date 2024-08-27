import requests
import json
import sys
import os

# switch okta app assignments for a user between group/user

# run this as `python change-assignments.py someone@domain.com user` to change to user `python change-assignments.py someone@domain.com group`

base_apps_url = "https://domain.okta.com/api/v1/apps"
base_users_url = "https://domain.okta.com/api/v1/users"

# this relies on OKTA_TOKEN in env file, if you don't have that, sub out the token here
token = os.environ.get('OKTA_TOKEN')

# accept email being targeting as input 1
## and the assignment preference of user or group as input 2
user_email = sys.argv[1]
assignment = sys.argv[2]

# construct the headers for the requests
def make_headers():
	headers = {}
	headers['Authorization'] = f'SSWS {token}'
	headers['Accept'] = 'application/json'
	headers['Content-Type'] = 'application/json'
	return(headers)

# get the user ID from the email by searching the email and returning the okta ID
# should add in an error handle here if can't find anything
def find_user(user_email):	
	url = base_users_url + "?q=" + user_email	
	headers=make_headers()
	response = requests.request("GET", url, headers=headers)
	body = json.loads(response.text)
	id = body[0]['id']
	return(id)

# list out the users assigned apps into the okta app IDs
def list_apps(find_user):
	user_id = find_user(user_email)
	url = base_apps_url + "?filter=user.id+eq+\"" + user_id + "\""
	headers=make_headers()
	app_list = []
	while url:
		response = requests.request("GET", url, headers=headers)
		body = json.loads(response.text)
		for app in body:
			app_id = app['id']
			app_list.append(app_id)
		if 'next' in response.links:
			url = response.links['next']['url']
		else:
			url = None
	return(app_list)


# change the assignments of the apps
def main():
	# get the list of okta app IDs
	app_list = list_apps(find_user)
	# get the okta user ID
	user_id = find_user(user_email)
	headers=make_headers()
	payload = {}
	# create variable of target_scope as empty for now
	target_scope = ""
	# if its group make variable GROUP, if not make USER
	# this could probably be changed to an ELIF for user and error if anything but group or user
	if assignment.lower() == "group":
		target_scope = "GROUP"
	else:
		target_scope = "USER"
	# create the body	
	payload['scope'] = target_scope
	payload['id'] = user_id
	payload_json = json.dumps(payload)
	# for each app ID
	for app_id in app_list:
		# set the URL with the app ID in
		url = base_apps_url + "/" + app_id + "/users"
		# post to the URL with the body of user/group
		response = requests.request("POST", url, headers=headers, data=payload_json)

		

if __name__ == "__main__":
    main()