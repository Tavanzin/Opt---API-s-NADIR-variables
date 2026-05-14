import requests
import base64

USERNAME = "tavan"
PASSWORD = "W@llacypaulo08"
credentials = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()

auth_url = "https://urs.earthdata.nasa.gov/api/users/"

url = "https://urs.earthdata.nasa.gov/api"

def get_access_token():
  get_token_url = auth_url + 'token'
  headers = { "Authorization": f"Basic {credentials}"}

  Token = requests.post(get_token_url, headers=headers)
  return Token.json().get("access_token")

def revoke_token(Token: str):
  revoke_url = auth_url + f"revoke_token?token={Token}"
  headers = {"Authorization": f"Basic {credentials}"}
  requests.post(revoke_url, headers=headers)
  return

def earthdataTest():
  Token = get_access_token()
  headers = { "Authorization": f"Bearer {Token}"}
  
  response = requests.post(url, headers=headers)
  
  revoke_token(Token)
  return {"status": response.status_code, "body": response.text}
