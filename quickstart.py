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

def get_service_access_token():
    token_url = 'https://mydatahelps.org/identityserver/connect/token' 

    assertion = {
      "iss": service_account_name,
      "sub": service_account_name,
      "aud": token_url,
      "exp": datetime.now().timestamp() + 900,
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


# Query all participants
def get_participants(
    access_token: str,
    query_params: Optional[Dict[str, str]] = None
) -> requests.Response:
    if query_params is None:
        query_params = {}

    headers = {
        "Authorization": f'Bearer {access_token}',
        "Accept": "application/json",
        "Content-Type":  "application/json; charset=utf-8"
    }
    url = f'https://mydatahelps.org/api/v1/administration/projects/{project_id}/participants'

    response = requests.get(url=url, params=query_params, headers=headers)
    response.raise_for_status()
    return response

# Query for a specific participant by participant identifier
def get_participant(
    access_token: str,
    participant_identifier: str
) -> requests.Response:

    headers = {
        "Authorization": f'Bearer {access_token}',
        "Accept": "application/json",
        "Content-Type":  "application/json; charset=utf-8"
    }
    url = f'https://mydatahelps.org/api/v1/administration/projects/{project_id}/participants/{participant_identifier}'

    response = requests.get(url=url, headers=headers)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response
    
token = get_service_access_token()
print(f'Obtained service access token:\n{token}')

data = get_participants(token)
participants = data.json()['totalParticipants']
print(f'\n\nTotal participants: {participants}')

participant_id = "PT-123"
data = get_participant(token, participant_id)
if data == None:
  print(f'Participant {participant_id} not found.')
else:
  participant = data.json()
  id = participant['id']
  print(f'Participant {participant_id} found with MDH ID {id}')
