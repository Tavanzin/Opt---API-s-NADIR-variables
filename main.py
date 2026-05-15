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
import asyncio

app = FastAPI()

@app.get("/ndvi")
async def call_script_ndvi(north: float = 42.3, south: float = 36.8, west: float = -9.7, east: float = -6.1):
    quadrantes = get_coordinates(north, south, west, east)
    
    nomes = list(quadrantes.keys())
    coords = list(quadrantes.values())

    resultados = await asyncio.gather(*[get_ndvi(c) for c in coords])

    responses = dict(zip(nomes, resultados))

    ### Pega a primeira e ultima data para o nome do ficheiro
    try:
        primeiro_quadrante = list(responses.values())[0]
        lista_dados = primeiro_quadrante.get("data", [])
        
        if lista_dados:
            # O primeiro "from" da lista
            data_inicio = lista_dados[0]["interval"]["from"].split('T')[0]
            # O último "to" da lista
            data_fim = lista_dados[-1]["interval"]["to"].split('T')[0]
        else:
            data_inicio = data_fim = "N/A"
    except (IndexError, KeyError):
        data_inicio = data_fim = "Erro ao extrair datas"

    ### cria ficheiro .json e cria na pasta do programa
    with open(f"outputs/{data_inicio}_{data_fim}-NDVI-{north}-{south}-{west}-{east}.json", "w", encoding="utf-8") as f:
       json.dump(responses, f, indent=4, ensure_ascii=False)

    return responses

@app.get("/fapar")
async def call_script_fapar(north: float = 42.3, south: float = 36.8, west: float = -9.7, east: float = -6.1):
  quadrantes = get_coordinates(north, south, west, east)

  nomes = list(quadrantes.keys())
  coords = list(quadrantes.values())

  restultados = await asyncio.gather(*[get_fapar(c) for c in coords])

  responses = dict(zip(nomes, restultados))

  try:
    primeiro_quadrante = list(responses.values())[0]
    lista_dados = primeiro_quadrante.get("data", [])
        
    if lista_dados:
      # O primeiro "from" da lista
      data_inicio = lista_dados[0]["interval"]["from"].split('T')[0]
      # O último "to" da lista
      data_fim = lista_dados[-1]["interval"]["to"].strip('T')[0]
    else:
      data_inicio = data_fim = "N/A"
  except (IndexError, KeyError):
      data_inicio = data_fim = "Erro ao extrair datas"

  with open(f"outputs/{data_inicio}_{data_fim}-fapar-{north}-{south}-{west}-{east}.json", "w", encoding="utf-8") as f:
     json.dump(responses, f, indent=4, ensure_ascii=False)

  return responses

@app.get("/Lai")
async def call_script_lai(north: float = 42.3, south: float = 36.8, west: float = -9.7, east: float = -6.1):
  quadrantes = get_coordinates(north, south, west, east)

  nomes = list(quadrantes.keys())
  coords = list(quadrantes.values())

  resultados = await asyncio.gather(*[get_lai(c) for c in coords])

  responses = dict(zip(nomes, resultados))

  try:
      primeiro_quadrante = list(responses.values())[0]
      lista_dados = primeiro_quadrante.get("data", [])

      if lista_dados:
        # O primeiro "from" da lista
        data_inicio = lista_dados[0]["interval"]["from"].split('T')[0]
        # O último "to" da lista
        data_fim = lista_dados[-1]["interval"]["to"].split('T')[0]
      else:
         data_inicio = data_inicio = "N/A"
         print("asdawda", data_inicio)
  except:
        data_inicio = data_fim  = "Erro ao extrair datas"


  with open(f"outputs/{data_inicio}_{data_fim}-lai-{north}-{south}-{west}-{east}.json", "w", encoding="utf-8") as f:
     json.dump(responses, f, indent=4, ensure_ascii=False)

  return responses

@app.get("/dem")
async def call_script_dem():
  response = get_dem()
  res = response["Response"]
  return Response(content=res.content, media_type="image/tiff")
 
@app.get("/modis/data")
async def call_script_modis(band: str = 'ET_500m', lat: float = 39.7, lon: float = -8.1, start_date: str = '2025001', end_date: str = '2025009'):
      response = get_modis(band, lat, lon, start_date, end_date)
      return response

#lat: float = 39.7, lon: float = -8.1, start_date: str = "2025-01-01", end_date: str = "2025-01-31", product: str = "MOD16A2"
@app.get("/modis/download")
async def call_script_modisDownload():
  response = earthdataTest()
  return response
