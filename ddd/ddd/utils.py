# ddd/utils.py
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from rest_framework.exceptions import AuthenticationFailed

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
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # Handle token expiration error
        raise AuthenticationFailed('Token has expired')  
    except jwt.DecodeError:
        # Handle token verification error
        raise AuthenticationFailed('Token is invalid')  
