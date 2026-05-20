import httpx
from dotenv import load_dotenv
import os

load_dotenv()

async def get_Copernicus_accessToken():

  client_id = os.getenv("COPERNICUS_CLIENT_ID")
  client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")

  print("asdawdad", client_secret)

  async with httpx.AsyncClient() as client:
    Token = await client.post(
      url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",

      data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
      }
    )
  return Token.json().get("access_token")
