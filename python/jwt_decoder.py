import jwt
import json
import requests

'''
decodes the jwt in the data.zta file
validates the signature against CS public key
this is the file that okta verify validates agains
'''


def decode_and_verify_jwt(token):
    try:
        # open the data.zta file
        with open(file_path, 'r') as file:
            # clean up the jwt
            token = file.read().strip()
        # get the header from the jwt
        header = jwt.get_unverified_header(token)
        # decode the jwt and get the jwk_url value
        jwks_url = jwt.decode(token, options={"verify_signature": False})['jwk_url']
        # get the json from the url
        # "https://assets-public.falcon.crowdstrike.com/zta/jwk.json"
        jwks = requests.get(jwks_url).json()
        public_key = None
        for key in jwks['keys']:
            if key['kid'] == header['kid']:
                # get the public key for the key that matches the kid from the header
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                break  # exit once matched

        if public_key:
            # if the key is present, decode the payload
            # we don't strictly need to decode with the key
            # we could just decode from base64
            # but in this case we wanna only do it with the key present
            payload = jwt.decode(token, public_key, algorithms=['RS256'])
            return header, payload
        else:
            # if no key is found, exit and report issue
            print("no key found")
            return None, None

    except jwt.ExpiredSignatureError:
        # if the attempt to decode the payload gives expired signature error
        print("expired")
        return None, None
    except jwt.InvalidTokenError:
        # if the token itself it invalid when trying to decrupt
        print("invalid token")
        return None, None
    except requests.exceptions.RequestException:
        # if the call to get the key from CS fails
        print("error with request")
        return None, None


def format_json(data):
    # formats the json object returned to look nice
    return json.dumps(data, indent=4)


# path to the data.zta file
file_path = "/Library/Application Support/Crowdstrike/ZeroTrustAssessment/data.zta"

# decode the jwt containedin the file
header, payload = decode_and_verify_jwt(file_path)

# if the header and payload are returned not empty
# then print on screen both, formatted json
if header and payload:
    print("header is:")
    print(format_json(header))
    print("\npayload is:")
    print(format_json(payload))
