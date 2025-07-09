import os
from libs.functions import okta_api_call, get_okta_token_read_only

'''
set the global variables
and get the token
we can get one token and use for all of this as it shouldn't take too long
if the export is for an exceptionally large group
maybe try moving to get a new token in the "write_user_factors"
'''
scopes = "okta.users.read okta.groups.read"
bearer_token = get_okta_token_read_only(scopes)
token = f"Bearer {bearer_token}"
method = 'get'

domain = "example"
base_url = f"https://{domain}.okta.com/api/v1"

# path to output to
file_path = "~/Downloads/factor_report.csv"

# create the CSV with headers
with open(os.path.expanduser(file_path), 'w') as file:
    file.write(
        '"email","factorType","status","created",'
        '"name","platform","deviceType"\n'
        )


# function to get the list of users from the okta group input
# return the list with user id, username
def get_users(group_id):
    '''
    list out all users in okta group
    input the group ID
    '''
    users_list = []
    users_url = f"{base_url}/groups/{group_id}/users"
    users = okta_api_call(users_url, token, method)
    for user in users:
        user_id = f'{user["id"]}'
        username = f'{user["profile"]["login"]}'
        users_list.append([user_id, username])
    return users_list


def write_user_factors(user_list):
    '''
    take each user and read their enrolled factors
    will put each factor per line with username ahead of it
    '''
    with open(os.path.expanduser(file_path), 'a') as file:
        for user in user_list:
            user_id = user[0]
            username = user[1]
            factors_url = f"{base_url}/users/{user_id}/factors"
            factors = okta_api_call(factors_url, token, method)
            for factor in factors:
                '''
                if the factor type is signed_nonce (okta fastpass)
                output with as much info as possible
                signed_nonce will have the most info to get
                '''
                if factor["factorType"] == "signed_nonce":
                    new_line = (
                        f'"{username}","{factor["factorType"]}",'
                        f'"{factor["status"]}","{factor["created"]}",'
                        f'"{factor["profile"]["name"]}",'
                        f'"{factor["profile"]["platform"]}",'
                        f'"{factor["profile"]["deviceType"]}"\n'
                        )
                    file.write(new_line)
                elif factor["factorType"] == "webauthn":
                    '''
                    if the type is webauthn
                    check if there is the "profile" key
                    if there is, get the info in there
                    if not, get the other stuff and put n/a
                    '''
                    profile_data = factor.get("profile")
                    if profile_data:
                        new_line = (
                            f'"{username}","{factor["factorType"]}",'
                            f'"{factor["status"]}","{factor["created"]}",'
                            f'"{factor["profile"]["authenticatorName"]}",'
                            f'"{factor["vendorName"]}",'
                            f'"n/a"\n'
                            )
                        file.write(new_line)
                    else:
                        new_line = (
                            f'"{username}","{factor["factorType"]}",'
                            f'"{factor["status"]}","{factor["created"]}",'
                            f'"n/a","{factor["vendorName"]}",'
                            f'"n/a"\n'
                            )
                        file.write(new_line)
                else:
                    '''
                    if its any other than signed_nonce or webauthn
                    get and output the most basic info available
                    '''
                    new_line = (
                        f'"{username}","{factor["factorType"]}",'
                        f'"{factor["status"]}","{factor["created"]}",'
                        f'"{factor["provider"]}","n/a",'
                        f'"n/a"\n'
                        )
                    file.write(new_line)


if __name__ == "__main__":
    group_id = "00--group-id--000"  # input group ID wanted here
    user_list = get_users(group_id)
    csv_output = write_user_factors(user_list)
    message = """Export complete, file in Downloads.
    signed_nonce is Okta FastPass.
    for webauthn with name authenticator, it is likely iCloud Keychain

    webauthn can show pending_activation,
    this is relatively rare where enrollment is incomplete"""
    print(message)
