from fastapi import FastAPI, Response

### Chamando funções ###
from scripts.ndvi import get_ndvi
from scripts.fapar import get_fapar
from scripts.Lai import get_lai
from scripts.dem import get_dem
from scripts.modis import get_modis
from scripts.modisDownload import earthdataTest
from divideCoordinates import get_coordinates

import json

app = FastAPI()

@app.get("/ndvi")
async def call_script_ndvi(north: float = 42.3, south: float = 36.8, west: float = -9.7, east: float = -6.1):
    quadrantes = get_coordinates(north, south, west, east)
    responses = {}

    for nome, coords in quadrantes.items():
      print("coordinates: ", coords)
      data = get_ndvi(coords)
      responses[nome] = data

    with open(f"Teste.json", "w", encoding="utf-8") as f:
       json.dump(responses, f, indent=4, ensure_ascii=False)

    return responses

@app.get("/fapar")
async def call_script_fapar(north: float = 42.3, south: float = 36.8, west: float = -9.7, east: float = -6.1):
  quadrantes = get_coordinates(north, south, west, east)
  responses = {}
  for nome, coords in quadrantes.items():
     data = get_fapar(coords)
     responses[nome] = data
  return responses

@app.get("/Lai")
async def call_script_lai(north: float = 42.3, south: float = 36.8, west: float = -9.7, east: float = -6.1):
  quadrantes = get_coordinates(north, south, west, east)
  responses = {}
  for nome, coords in quadrantes.items():
      print("coordinates: ", coords)
      data = get_lai(coords)
      responses[nome] = data
  return responses

@app.get("/dem")
async def call_script_dem():
  response = get_dem()
  res = response["Response"]
  return Response(content=res.content, media_type="image/tiff")
 
@app.get("/modis/data")
async def call_script_modis(band: str = 'ET_500m', lat: float = 39.7, lon: float = -8.1, start_date: str = '2025001', end_date: str = '2025009'):
      response = get_modis(band, lat, lon, start_date, end_date)

      subset = response.json().get("subset", [])
      result = []

      for item in subset:
        values = item.get("data", [])

        validValue = [v for v in values if v > -9000 & v < 32700]

        if validValue:
           mean = sum(validValue) / len(validValue)
        
        else:
           mean = 0

        result.append({
           "calendar_date": item["calendar_date"],
          "average_value": round(mean, 2),
          "pixel_count": len(validValue)
        })

      return result

#lat: float = 39.7, lon: float = -8.1, start_date: str = "2025-01-01", end_date: str = "2025-01-31", product: str = "MOD16A2"
@app.get("/modis/download")
async def call_script_modisDownload():
  response = earthdataTest()
  return response
