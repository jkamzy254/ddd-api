# ddd/utils.py
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from rest_framework.exceptions import AuthenticationFailed
from django.db import connection

from pyfcm import FCMNotification
import firebase_admin
from firebase_admin import credentials, messaging
import json

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os

firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
print("FIREBASE CREDENTIALS: ", firebase_creds)

FIREBASE_CREDENTIALS = json.loads(firebase_creds)

if FIREBASE_CREDENTIALS:
    cred_dict = FIREBASE_CREDENTIALS
    cred = credentials.Certificate(cred_dict)
        
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

def encode_jwt(payload):
    # Load the private key
    with open('ddd/config/private_key.pem', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # No password for the private key
        )

    # Define the payload (customize it according to your needs)
    # Generate the JWT using RS256 algorithm
    token = jwt.encode(payload, private_key, algorithm='RS256')

    return token

def decode_jwt(req):
    token = req.headers.get("authorization", None)
    if not token:
        raise AuthenticationFailed('Unauthorized!')
    token = token.split(" ")[1]
    # Load the public key
    with open('ddd/config/public_key.pem', 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read()
        )

    try:
        # Verify and decode the JWT using the public key
        # payload = jwt.decode(token, public_key, algorithms=["RS256"])
        payload = jwt.decode(token, options={"verify_signature": False}, algorithms=["RS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # Handle token expiration error
        raise AuthenticationFailed('Token has expired')  
    except jwt.DecodeError:
        # Handle token verification error
        raise AuthenticationFailed('Token is invalid')  

    
def send_push_notification(uid, title, body):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT token FROM FCMTokenTable WHERE UID = %s ORDER BY ID DESC", [uid]
            )
            tokens = [row[0] for row in cursor.fetchall()]
        
        if not tokens:
            return {'status': 'error', 'message': 'No tokens found for the user'}

        res = []
        for token in tokens:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=token
            )

            response = messaging.send(message)
            res.append(response)

        return {'status': 'success', 'results': res}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}