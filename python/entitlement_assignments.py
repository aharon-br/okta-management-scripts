from libs.functions import okta_api_call, get_okta_token_read_only
import os
import csv

'''
v. 1
there doesn't seem any great way to get entitlements
listed for all users to an applications
this will read all the users
then one by one read their entitlements and output a CSV
the output isn't super clean right now but it works
change the app_id for which app you want to list out
'''

scopes = "okta.apps.read okta.governance.entitlements.read"
bearer_token = get_okta_token_read_only(scopes)
token = f"Bearer {bearer_token}"
# token = get_local_okta_admin_token()
method = 'get'

# change the domain and app ID as needed
domain = "example"
base_url = f"https://{domain}.okta.com"
app_id = '00--app--id--00'


def get_users(app_id):
    '''
    lists out all the users assigned to the app
    gives email and okta user id
    '''
    users_list = []
    app_url = f"{base_url}/api/v1/apps/{app_id}/users"
    users = okta_api_call(app_url, token, method)
    for user in users:
        user_id = f'{user["id"]}'
        username = f'{user["credentials"]["userName"]}'
        users_list.append([user_id, username])
    return users_list


def get_user_entitlements(user_list, app_id):
    '''
    take each user assigned the app_id
    read their entitlements using the okta governance API
    this API is heavily rate limited
    we need to do one call per user
    this might take a while....
    '''
    governance_url = f"{base_url}/governance/api/v1/principal-entitlements"
    # create an empty list called entlmnt that we'll put the entitlements into
    entlmnt = []
    headers = ["username", "entitlements"]
    entlmnt.append(headers)
    for user in user_list:
        user_id = user[0]
        user_name = user[1]
        # construct the filter term for the query
        # the OIG API is a little different to the general okta admin API
        raw_filter = (
            f'parent.externalId eq "{app_id}" AND parent.type eq '
            f'"APPLICATION" AND targetPrincipal.externalId eq "{user_id}" '
            f'AND targetPrincipal.type eq "OKTA_USER"'
            )
        query = {
            "filter": raw_filter
            }
        data = None
        # get the entitlements for the user
        user_entitlements = okta_api_call(governance_url, token, method, data, query)
        entitlement_names = []
        for item in user_entitlements.get("data",):
            for value in item.get("values",):
                entitlement_names.append(value.get("name"))
        # add any found to the entlmnt list
        entlmnt.append([user_name, entitlement_names])
    return entlmnt


if __name__ == "__main__":
    user_list = get_users(app_id)
    entlmnt = get_user_entitlements(user_list, app_id)
    # output the list in entlmnt to a csv
    file_path = "~/Downloads/entitlements.csv"
    with open(os.path.expanduser(file_path), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(entlmnt)
    print("Export complete, file in Downloads")
