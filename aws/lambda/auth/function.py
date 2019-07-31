from __future__ import print_function
import json
import logging
import requests
import time
from jose import jwt, jwk
from jose.utils import base64url_decode
import boto3


# def lambda_handler(event, context):
#     # TODO implement
#     print("from lambda_handler: %s %s" % (repr(event),repr(context)))
#     logging.error("blabla")
#     print("arf")
#     # TODO: write code...
#     return {
#         'statusCode': 200,
#         'body': json.dumps('Hello from Lambda seb!'),
#         'event': json.dumps(event),
#     }


region = 'us-west-2'
userpool_id = 'us-west-2_KAglRSC16'
app_client_id = '668qr87fc875enqadve7o4fno7'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
keys = requests.get(keys_url).json()['keys']
cogidp = boto3.client('cognito-idp')
user = cogidp.admin_get_user(UserPoolId=userpool_id,
                                 Username="sebastien.lelong@gmail.com")
print(user)

 
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
    print("user: %s" % user)
 

def lambda_handler(event, context):
    try:
        # Verify and get information from token
        # it can be in headers or as qs
        token = ""
        if event.get("headers",{}).get("authorization"):
            token = event["headers"]['authorization']
        elif event.get("queryStringParameters",{}).get("auth"):
            token = event["queryStringParameters"]["auth"]
        claims = is_token_valid(token)
        print(claims)
        if claims:
            # Get principalId from idInformation
            principalId = claims['sub']
            print("Token valid")
            is_user_has_permissions(principalId,event['methodArn'])
            return generatePolicy(principalId, 'Allow', event['methodArn'])

        return generatePolicy(None, 'Deny', event['methodArn'])
 
    except Exception as err:
        # Deny access if the token is invalid
        print(err)
        return generatePolicy(None, 'Deny', event.get('methodArn',"arn:null"))
 

# the following is useful to make this script executable in both
# AWS Lambda and any other local environments
if __name__ == '__main__':
    # for testing locally you can enter the JWT ID Token here
    #t = """eyJraWQiOiJpNGhTMDd2ZDBvQmowdGV5K05wTnVKQWd2VVhUVTF2Qm9tRVQ3dHVhRStFPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIyM2Q5MWI2Yi04YzFhLTRlMGUtYWQ4My0wOWIxMmMwNDg1MDgiLCJldmVudF9pZCI6IjgzZjI0NDExLTQwN2
    t = """eyJraWQiOiJpNGhTMDd2ZDBvQmowdGV5K05wTnVKQWd2VVhUVTF2Qm9tRVQ3dHVhRStFPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIyM2Q5MWI2Yi04YzFhLTRlMGUtYWQ4My0wOWIxMmMwNDg1MDgiLCJldmVudF9pZCI6ImJlYWYyZmJjLTA4YzEtNDQ4OC1iZTg0LTA0OGY5MmI1MTY2YyIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE1NjQwODQyMTAsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy13ZXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtd2VzdC0yX0tBZ2xSU0MxNiIsImV4cCI6MTU2NDA4NzgxMCwiaWF0IjoxNTY0MDg0MjEwLCJqdGkiOiI5MGNlMjE4Ny04Mzk2LTQ0ZjYtYmQ0MC0yNTIyZWJiZTFkNjQiLCJjbGllbnRfaWQiOiI2Njhxcjg3ZmM4NzVlbnFhZHZlN280Zm5vNyIsInVzZXJuYW1lIjoiMjNkOTFiNmItOGMxYS00ZTBlLWFkODMtMDliMTJjMDQ4NTA4In0.BBmZmVvjz00EfpbdCXHKmE-KVCwRkyQw4swjPmIpKgA-XPpeu-E8mtwDSEC5CPSSkGg0xggTAz7l1rf3Jcc4HZy1hJ5zRY1R0GnmIzGluFe2v8cHDI4cXLO65yCyfjaHYP0OAlVF3B78IgoEY2T3MSXv6Q10mD7_NZCF2W_WPSJOAmpsaBjlgmFHS-O7n2U5cWd9XlBeaqOa0O7vUeLrGEsQVb6ZBDbtw3yIUps2uQwlp8g6-ox4zPHCAaUinxHy2mp7p3sNXT5DDqgru4dqVwVFPJ6HQlEaZMtga5AXBY_4lC_oG-A3kLc--Wcn984dguWsGqP5ogjyuv2pLOt8KA"""
    event = {'authorizationToken': t, "methodArn": "arn:test"}
    policy = lambda_handler(event, None)
    print(policy)
