import json

import requests
import jwt
from jwt.algorithms import RSAAlgorithm
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from config.settings import AUTH0_DOMAIN, OIDC_OP_AUDIENCE


AUTH0_DOMAIN = "dev-1jlpucnk4u6by33k.us.auth0.com"
OIDC_OP_AUDIENCE = "https://my-api.local"  # Change to your API identifier in Auth0

class Auth0JSONWebTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return None

        try:
            scheme, token = auth.split()
            if scheme.lower() != 'bearer':
                raise AuthenticationFailed('Invalid auth header')
        except ValueError:
            raise AuthenticationFailed('Invalid auth header')

        try:
            # Fetch JWKS
            jwks_url = f'https://{AUTH0_DOMAIN}/.well-known/jwks.json'
            jwks = requests.get(jwks_url).json()
            unverified_header = jwt.get_unverified_header(token)

            rsa_key = {}
            for key in jwks['keys']:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
                    break

            if not rsa_key:
                raise AuthenticationFailed('Unable to find appropriate key')

            # Convert to PEM-formatted key
            public_key = RSAAlgorithm.from_jwk(json.dumps(rsa_key))

            # Decode the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=OIDC_OP_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            #
            # Dummy user object (customize or integrate with your user model)
            print(payload)
            for key, value in payload.items():
                print(f"{key}: {value}")
            user = type('User', (), {
                "id": payload['sub'],
                "email": payload.get("email", ""),
                "is_authenticated": True
            })()

            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            raise AuthenticationFailed(f'Auth0 JWT Error: {str(e)}')

        return None