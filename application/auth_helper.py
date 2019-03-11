from functools import wraps
from flask import abort, request
import requests
import json
import time
from jose import jwk, jwt
from jose.utils import base64url_decode

region = 'us-west-2'
userpool_id = 'us-west-2_gAjMkmuFh'
app_client_id = '7uh22ggsabjjusnb8fqdfitkf8'
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)
response = requests.get(keys_url)
keys = response.json()['keys']

def decode_verify_jwt(token):
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
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        if not 'Authorization' in request.headers:
            print("no Authorization in request.headers")
            abort(401)
        
        token = request.headers.get('Authorization')
        try:
            user = decode_verify_jwt(token)
        except:
            print("exception when decoding/verifying jwt token")
            abort(401)
        if not user: 
            abort(401)
        
        return f(*args, **kws)
    return decorated_function