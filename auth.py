import httpx

CLIENT_ID = "sh-f20ada3b-35dc-42c7-a279-2ef53e06c5b8"
CLIENT_SECRET = "svZmZBPwFjwnX3GZGoJgugad0hzmANtM"

async def get_access_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "client_credentials"
            }
        )
    return response.json().get("access_token")
