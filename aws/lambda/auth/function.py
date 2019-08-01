import boto3
import json
import logging
import requests
import time
import re
from jose import jwt, jwk
from jose.utils import base64url_decode
from arnparse import arnparse

region = 'us-west-2'
userpool_id = 'us-west-2_KAglRSC16'
app_client_id = '668qr87fc875enqadve7o4fno7'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
keys = requests.get(keys_url).json()['keys']
cogidp = boto3.client('cognito-idp')

 
def generatePolicy(principalId, effect, methodArn):
    authResponse = {}
    authResponse['principalId'] = principalId
 
    if effect and methodArn:
        policyDocument = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'FirstStatement',
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': methodArn
                }
            ]
        }
 
        authResponse['policyDocument'] = policyDocument
 
    return authResponse

def is_token_valid(token):
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:                                                                                                                                                                   
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['client_id'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims


def is_user_has_permissions(username,methodArn):
    print("method %s" % methodArn)
    cogidp = boto3.client('cognito-idp')
    user = cogidp.admin_get_user(UserPoolId=userpool_id,
                                 Username=username)
    # extract registered api on user's profile
    attrs = user["UserAttributes"]
    btnames = [a["Value"] for a in attrs if a["Name"] == "custom:biothings-api-name"]
    assert len(btnames) == 1, "No BioThings API listed in user attributes"
    btnames = btnames.pop()
    # it can be a comma separated list. comparison will be case-insensitive.
    btnames = [b for b in map(str.lower,map(str.strip,btnames.split(",")))]
    # user has to be confirmed
    assert user.get("UserStatus") == "CONFIRMED", "User not confirmed"
    # then the resource he's trying to access has to match his own biothings APIs
    arn = arnparse(methodArn)
    # arn resource iooks like "g4k1vo9uyi/beta/GET/farm/cgi/build_manager"
    # we want to extract "cgi". Position after HTTP verb and then extract part after /farm
    try:
        path = re.match(r".*/[A-Z]+/farm/(.+)",arn.resource).groups()[0]
        api_name = path.split("/")[0]
        assert api_name in btnames, "User not allowed to access API %s (allowed APIs: %s)" % (repr(api_name),btnames)
        print("Requested API '%s' in user's registered APIs %s" % (api_name,repr(btnames)))
    except Exception as e:
        print(e)
        raise Exception("Invalid arn resource: %s" % repr(arn.resource))
 

def lambda_handler(event, context):
    try:
        # Verify and get information from token
        # it can be in headers or as qs
        token = ""
        if event.get("headers",{}).get("x-biothings-access-token"):
            token = event["headers"]['x-biothings-access-token']
        elif event.get("queryStringParameters",{}).get("token"):
            token = event["queryStringParameters"]["token"]
        assert token, "No auth token found in event: %s" % repr(event)
        #print("token: %s" % token)
        claims = is_token_valid(token)
        #print(claims)
        if claims:
            print("Token valid")
            # Get principalId from idInformation
            principalId = claims['sub']
            is_user_has_permissions(principalId,event['methodArn'])
            print("User has permissions")
            return generatePolicy(principalId, 'Allow', event['methodArn'])

        return generatePolicy(None, 'Deny', event['methodArn'])
 
    except Exception as err:
        # Deny access if the token is invalid
        print("General error: %s" % err)
        import logging
        logging.exception(err)
        return generatePolicy(None, 'Deny', event.get('methodArn',"arn:null"))
 

# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    t = """eyJraWQiOiJpNGhTMDd2ZDBvQmowdGV5K05wTnVKQWd2VVhUVTF2Qm9tRVQ3dHVhRStFPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIyM2Q5MWI2Yi04YzFhLTRlMGUtYWQ4My0wOWIxMmMwNDg1MDgiLCJldmVudF9pZCI6ImVhMWY2OTUxLTY4YjItNDBkYi1hZDJhLTJhNjNkNzZkNTNhMiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE1NjQ1OTAxNzEsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy13ZXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtd2VzdC0yX0tBZ2xSU0MxNiIsImV4cCI6MTU2NDU5Mzc3MSwiaWF0IjoxNTY0NTkwMTcxLCJqdGkiOiJjZWQ0NThkMS1hZGZjLTRlYTYtYTBkOS1kZjhkNjdkZDViMzgiLCJjbGllbnRfaWQiOiI2Njhxcjg3ZmM4NzVlbnFhZHZlN280Zm5vNyIsInVzZXJuYW1lIjoiMjNkOTFiNmItOGMxYS00ZTBlLWFkODMtMDliMTJjMDQ4NTA4In0.iUTpOnRMzXf51T2OELMVQALQBDKTfCOfa6lG_t5vIJUAdj9j7_Ww3ULbPUnzk-hOYRYVhJB7i5ydIyViRDurikQMqmXbZ7IOwbFR3hjGa0nGZvekO9M5VPSAall4EOC3GkVVEvsQ4Cx9l2qtKmOv5cPF1pOtCGcQotkDPhzSfy71rbtmB2awyvdbto_aYTWMx8zVbPq37D2EOcRkK-xBq1EONWAJhNo_AEdsKhN6QNDwatf8yAoxJ6cs1MJOZ7iRaJsgy7Mbuwm_EII0IdMyRn6Ndixsxj2puK9fRpzquRbYbrbjIwrFFNer3Cst8UZE6MEeyCalf_GicGvRfmQe_Q"""
    arn = """arn:aws:execute-api:us-west-1:215751090072:g4k1vo9uyi/beta/GET/farm/cgi/build_manager"""
    event = {"headers" : {'x-biothings-access-token': t}}
    event["methodArn"] = arn
    policy = lambda_handler(event, None)
    print(policy)

