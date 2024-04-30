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

base_url = 'https://mydatahelps.org'
token_url = f'{base_url}/identityserver/connect/token' 

def get_service_access_token():

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


def get_from_api(
    service_access_token: str,
    resource_url: str,
    query_params: Optional[Dict[str, str]] = None,
    raise_error: bool = True # Raise an error automatically if response is not a success
) -> requests.Response:
    if query_params is None:
        query_params = {}

    headers = {
        "Authorization": f'Bearer {service_access_token}',
        "Accept": "application/json",
        "Content-Type":  "application/json; charset=utf-8"
    }
    
    url = f'{base_url}/{resource_url}'
    response = requests.get(url=url, params=query_params, headers=headers)
    
    if raise_error:
      response.raise_for_status()
      
    return response

# Get a participant access token for the specified participant
# Used for MyDataHelps Embeddables ONLY
def get_participant_access_token(
    service_access_token: str,
    participant_id: str,
    scopes: str
):

    token_payload = {
        "scope": scopes,
        "grant_type": "delegated_participant",
        "participant_id": participant_id,
        "client_id": "MyDataHelps.DelegatedParticipant",
        "client_secret": "secret",
        "token": service_access_token,
    }
    response = requests.post(url=token_url, data=token_payload)
    response.raise_for_status()
    return response.json()["access_token"]
    

# Get a service access token, needed for all API calls.
service_access_token = get_service_access_token()
print(f'Obtained service access token:\n{service_access_token}')

# Get all participants
url = f'/api/v1/administration/projects/{project_id}/participants'
response = get_from_api(service_access_token, url)
participants = response.json()['totalParticipants']
print(f'\n\nTotal participants: {participants}')

# Get a specific participant by identifier. We disable 'raise_error' here
# so we can handle the 404 case ourselves.
participant_identifier = "PT-123"
url = f'/api/v1/administration/projects/{project_id}/participants/{participant_identifier}'
response = get_from_api(service_access_token, url, {}, False)
if response.status_code == 404:
  print(f'Participant {participant_identifier} not found.')
else:
  participant = response.json()
  id = participant['id']
  print(f'Participant {participant_identifier} found with MDH ID {id}')
  
  # NOTE: This piece is only necessary when using MyDataHelps Embeddables in a custom app. 
  # Most API use cases do NOT require a participant token.
  scopes = "api user/*.read"
  participant_access_token = get_participant_access_token(service_access_token, id, scopes)
  print(f'Obtained participant access token for {id}: {participant_access_token}')
