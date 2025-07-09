import requests
import json
import os
from getpass import getpass
import time
import datetime
import jwt


def get_local_okta_admin_token():
    '''
    this grabs an admin token from the environment file
    this can be used where a full admin privilege is needed
    however, it does require having a personal token saved locally
    which isn't typically advised
    it looks for environment variable okta_token
    '''
    if os.environ.get('okta_token'):
        token = os.environ.get('okta_token')
        admin_token = f"SSWS {token}"
    else:
        token = getpass('no admin token in env file, paste api token here:\n')
        admin_token = f"SSWS {token}"
    return admin_token


def get_okta_token_read_only(scopes):
    '''
    v. 0.5
    interacts with API services app:
    granted many read-only scopes
    invoke with the scopes separated by spaces
    token can be used in API calls with prefix Bearer
        '''
    okta_domain = 'example'
    exp = time.time() + 60*60  # set the token expiration, max is one hour
    clientid = '00-client-id-00'  # the client id from the app
    aud = f"https://{okta_domain}.okta.com/oauth2/v1/token"
    # this uses ... app name
    payload = {
              "iss": clientid,
              "sub": clientid,
              "aud": aud,
              "exp": exp
              }
    privatekey = """
    ---THE KEY GOES IN HERE---
    """
    # create the jwt
    encoded_token = jwt.encode(payload, privatekey, algorithm='RS256')
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
        }  # construct the headers
    body = {
        'grant_type': 'client_credentials',
        'scope': scopes,
        'client_assertion_type':
        'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
        'client_assertion': encoded_token
        }  # construct the body, with the scope and jwt
    # change the scopes above if more or less are needed
    token_url = f"https://{okta_domain}.okta.com/oauth2/v1/token"
    response = requests.post(
        token_url,
        headers=headers,
        data=body
        )  # post to get the token
    json_body = json.loads(response.content)  # get the body in json
    return json_body['access_token']  # read the access_token key value


def okta_api_call(url, token, method='', data=None, query=None):
    '''
    v. 1
    will return single object or handle pagination and return full list on GET
    adapted with gratitude from
    '''
    # using sessions should be a little faster
    session = requests.Session()
    # set the headers for the API
    headers = {
        "authorization": token,
        "Content-Type": "application/json",
        "accept": "application/json"
        }
    other_methods = ["post", "put", "patch"]
    if method.lower() in other_methods:
        session_method = getattr(session, method.lower())
        while True:
            response = session_method(url, headers=headers, json=data, params=query)
            try:
                response.raise_for_status()  # raise error if not 200
                output = response.json()
            except requests.exceptions.HTTPError as error:
                if response.status_code == 429:
                    response = error.response
                    retry_after_epoch = response.headers.get('x-rate-limit-reset')
                    reset_time = datetime.datetime.fromtimestamp(int(retry_after_epoch))
                    now = datetime.datetime.now()
                    wait_time = (reset_time - now).total_seconds()
                    if wait_time > 0:
                        wait_time_int = int(wait_time)
                        print(
                            f"Rate limit exceeded. \
                            Retrying after {wait_time_int} seconds..."
                            )
                        time.sleep(wait_time)
                        continue
                    else:
                        continue
                else:
                    raise error
            return output

    elif method.lower() == "get":
        # create an output array to be used if the items are a list
        output = []
        while url:
            response = session.get(url, headers=headers, params=query)
            try:
                # Raise error for bad responses (4xx or 5xx)
                response.raise_for_status()
                # Check if the response is a list
                body = response.json()
                if not isinstance(body, list):
                    # if its not a list, just return the body now and exit
                    return body
                # if it is a list, append each object to the output list
                for entity in body:
                    output.append(entity)
                # if there is a next page, set the URL to that and go again
                if 'next' in response.links:
                    url = response.links['next']['url']
                else:
                    url = None
            # if there is an error in the request, handle
            except requests.exceptions.HTTPError as error:
                '''
                if the error is 429, rate limit
                then get retry-after whatever okta says
                if okta doesn't say, just wait 10 seconds
                '''
                if response.status_code == 429:
                    response = error.response
                    retry_after_epoch = response.headers.get('x-rate-limit-reset')
                    reset_time = datetime.datetime.fromtimestamp(int(retry_after_epoch))
                    now = datetime.datetime.now()
                    wait_time = (reset_time - now).total_seconds()
                    if wait_time > 0:
                        wait_time_int = int(wait_time)
                        print(
                            f"Rate limit exceeded. \
                            Retrying after {wait_time_int} seconds..."
                            )
                        time.sleep(wait_time)
                        continue  # Retry the same request
                    else:
                        continue
                else:
                    # if its anything but 429, raise the error
                    raise error
        return output

    elif method.lower() == "delete":
        while True:
            response = session.delete(url, headers=headers, json=data, params=query)
            try:
                response.raise_for_status()  # raise error if not 200
                output = response.status_code
            except requests.exceptions.HTTPError as error:
                if response.status_code == 429:
                    response = error.response
                    retry_after_epoch = response.headers.get('x-rate-limit-reset')
                    reset_time = datetime.datetime.fromtimestamp(int(retry_after_epoch))
                    now = datetime.datetime.now()
                    wait_time = (reset_time - now).total_seconds()
                    if wait_time > 0:
                        wait_time_int = int(wait_time)
                        print(
                            f"Rate limit exceeded. \
                            Retrying after {wait_time_int} seconds..."
                            )
                        time.sleep(wait_time)
                        continue
                    else:
                        continue
                else:
                    raise error
            return output

    else:
        output = print(f"{method} is not recognized")
        return output
