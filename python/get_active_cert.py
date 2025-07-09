import os
import csv
import xml.etree.ElementTree as xmltree
import requests
from libs.functions import okta_api_call, get_okta_token_read_only

domain = "example"
base_url = f"https://{domain}.okta.com/api/v1/apps"
method = 'get'
scopes = "okta.apps.read"
bearer_token = get_okta_token_read_only(scopes)
token = f"Bearer {bearer_token}"
file_path = "~/Downloads/active_saml_app_creds.csv"


'''
this will read all active SAML apps in okta
it will :
1. get all credentials
2. get the active cert by simulating a SAML flow
3. compare and output which is the active one
4. this does a lotta calls, its a good chance to get rate limited a few times
'''


def clean_certificate(cert_string):
    '''
    Removes whitespace and newlines
    from the certificate when doing the
    saml assertion preview
    without cleaning this up, there wont be a match
    between that and the one in the app credentials
    '''
    if not isinstance(cert_string, str):
        # make sure its a string
        return ""
    return "".join(cert_string.split())


def get_apps():
    '''
    create a list of all apps
    label and app ID
    '''
    app_list = []  # create the empty array
    app_list_url = f"{base_url}"
    apps = okta_api_call(app_list_url, token, method, None, None)
    for app in apps:
        if (app.get("status") == "ACTIVE" and
            app.get("signOnMode") == "SAML_2_0"):
            app_id = f'{app["id"]}'
            app_label = f'{app["label"]}'
            app_list.append([app_label, app_id])
    return app_list


def saml_preview(app_id):
    '''
    get the SAML assertion and return the active cert
    '''
    saml_url = f"{base_url}/{app_id}/sso/saml/metadata"
    headers = {
        'accept': 'text/xml',
        'authorization': token
    }
    '''
    we need to do this without using the library okta call
    the library is set to accept and handle json only
    here we need xml
    '''
    response = requests.request("GET", saml_url, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(f"error: {error}")
        return None
    assertion = response.text
    # set the namespaces to look for in xml
    namespaces = {
        'md': 'urn:oasis:names:tc:SAML:2.0:metadata',
        'ds': 'http://www.w3.org/2000/09/xmldsig#'
    }
    parsed_xml = xmltree.fromstring(assertion)
    # get the vert with xml tree and then clen it up
    raw_cert = parsed_xml.find('.//ds:X509Certificate', namespaces)
    cert = clean_certificate(raw_cert.text)
    return cert


def get_cred_keys(app_id):
    '''
    get the list of credentials for the app
    this will give all as an a list
    '''
    creds_url = f"{base_url}/{app_id}/credentials/keys"
    creds = okta_api_call(creds_url, token, method)
    return creds


def compare_creds_to_cert(active_cert, creds_list):
    '''
    get the list of application credentials
    then compare that to the one returned within the SALM assertion
    output the details for the matching credentials
    '''
    for cred in creds_list:
        if cred['x5c']:
            '''
            the certificate itself is an array
            but within okta, it appears there is only ever one
            if this changes or proves to be inaccurate then
            this will need to be adjusted to do another for loop
            for now, i dont think thats needed
            '''
            cert_in_cred = cred['x5c'][0]
            if cert_in_cred == active_cert:
                kid = cred.get("kid")
                expire = cred.get("expiresAt")
                created = cred.get("created")
                return [kid, expire, created]
    return None


def create_csv(file_path):
    '''
    create a CSV with the headrs
    '''
    with open(os.path.expanduser(file_path), 'w', newline='') as file:
        header = ['AppLabel', 'AppID', 'KID', 'ExpiresAt', 'Created']
        writer = csv.writer(file)
        writer.writerow(header)


def write_to_csv(credential_info, file_path):
    '''
    take the credential info for each app passed to it
    write it out as a new line to the CSV
    '''
    if credential_info is None:
        return
    with open(os.path.expanduser(file_path), 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(credential_info)


def main():
    create_csv(file_path)  # create the CSV
    apps = get_apps()  # list out the apps
    for app in apps:
        app_label = app[0]  # label is first column
        app_id = app[1]  # app id is column two
        active_cert = saml_preview(app_id)  # do the assertion
        all_keys = get_cred_keys(app_id)  # get the creds
        # compare the assertion and creds
        active_key = compare_creds_to_cert(active_cert, all_keys)
        if active_key:
            # write out to the CSV
            line = [app_label, app_id] + active_key
            write_to_csv(line, file_path)
    print("complete, file in downloads")


if __name__ == "__main__":
    main()
