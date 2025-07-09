from libs.functions import okta_api_call, get_local_okta_admin_token
import csv

'''
this reads from a csv called entitlements.csv
it should have a column with emails called username
it should have a column with the bundle ID being assigned
this should be called bundle_id
other columns can be in the csv but wont be used
'''

domain = "example"
base_url = f"https://{domain}.okta.com/"

# we need to get an admin token here
# we are going to need to post to okta
token = get_local_okta_admin_token()


def get_user_id(user_email):
    # get the okta user id from the user email
    # we need the id for assignment of bundles
    users_url = base_url + "api/v1/users/" + user_email
    method = 'get'
    user = okta_api_call(users_url, token, method)
    user_id = user["id"]
    return user_id


def make_request_body(bundle_id, user_id):
    '''
    make the json body for the bundle assignment
    it will look like:
    {
        'grantType': 'ENTITLEMENT-BUNDLE',
        'entitlementBundleId': '12345',
        'actor': 'ACCESS_REQUEST',
        'targetPrincipal': {
            'externalId': '00abcdefg00',
            'type': 'OKTA_USER'
            }
    }
    '''
    body = {}
    body['grantType'] = 'ENTITLEMENT-BUNDLE'
    body['entitlementBundleId'] = bundle_id
    body['actor'] = 'ACCESS_REQUEST'
    body['targetPrincipal'] = {}
    body['targetPrincipal']['externalId'] = user_id
    body['targetPrincipal']['type'] = 'OKTA_USER'
    return body


def main():
    with open("entitlements.csv", "r", encoding="utf-8") as csvfile:
        # get the csv and go thru the rows and assign the bundles
        reader = csv.DictReader(csvfile)
        for row in reader:
            user_email = row["username"]
            user_id = get_user_id(user_email)
            bundle_id = row["bundle_id"]
            body = make_request_body(bundle_id, user_id)
            grant_url = base_url + "governance/api/v1/grants"
            data = body
            method = 'post'
            okta_api_call(grant_url, token, method, data)
            print(f"user {user_email} is complete")


if __name__ == "__main__":
    main()
