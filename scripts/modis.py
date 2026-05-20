import httpx
import json
import os

async def get_modis(band, lat, lon, start_date, end_date):
  url = (
        f"https://modis.ornl.gov/rst/api/v1/MOD16A2/subset?"
        f"latitude={lat}&longitude={lon}"
        f"&startDate=A{start_date}&endDate=A{end_date}"
        f"&product=MOD16A2&band={band}"
        f"&kmAboveBelow=5&kmLeftRight=5"
    )
  
  async with httpx.AsyncClient() as client:
     response = await client.get(url)
    
  data = response.json()

  pasta_destino = "outputs"
  if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

  caminho_ficheiro = os.path.join(pasta_destino, f"{start_date}_{end_date}-{band}-{lat}_{lon}.json")

  with open(caminho_ficheiro, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

  return data
