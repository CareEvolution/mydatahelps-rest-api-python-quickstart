from datetime import datetime
from uuid import uuid4
import os
from typing import Optional, Dict
import jwt  # pip install PyJWT   and  pip install cryptography
import requests  # pip install requests
from dotenv import load_dotenv # pip install python-dotenv

load_dotenv()

# Environment variables read from .env file
private_key = os.getenv('RKS_PRIVATE_KEY')
service_account_name = os.getenv('RKS_SERVICE_ACCOUNT')
project_id = os.getenv('RKS_PROJECT_ID')

def get_token():
    token_url = 'https://mydatahelps.org/identityserver/connect/token' 

    assertion = {
      "iss": service_account_name,
      "sub": service_account_name,
      "aud": token_url,
      "exp": datetime.now().timestamp() + 200,
      "jti": str(uuid4()),
    }
    signed_assertion = jwt.encode(payload=assertion, key=private_key, algorithm="RS256")
    token_payload = {
      "scope": "api",
      "grant_type": "client_credentials",
      "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
      "client_assertion": signed_assertion
    }
    response = requests.post(url=token_url, data=token_payload)
    response.raise_for_status()
    return response.json()["access_token"]


def get_from_api(
    access_token: str,
    resource_url: str,
    query_params: Optional[Dict[str, str]] = None
) -> requests.Response:
    if query_params is None:
        query_params = {}

    headers = {
        "Authorization": f'Bearer {access_token}',
        "Accept": "application/json",
        "Content-Type":  "application/json; charset=utf-8"
    }
    url = f'https://mydatahelps.org/api/v1/administration/projects/{project_id}{resource_url}'

    response = requests.get(url=url, params=query_params, headers=headers)
    response.raise_for_status()
    return response

token = get_token()
print(f'Obtained access token:\n{token}')

data = get_from_api(token, '/participants')
participants = data.json()['totalParticipants']
print(f'\n\nTotal participants: {participants}')
