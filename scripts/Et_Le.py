import httpx
import json
import os
import asyncio

from controllers.ModisController import fetch_modis, merge_responses, split_into_chunks

async def get_modis(band: str, lat: float, lon: float, start_date: str, end_date: str) -> dict:
  if band == 'Et' or band == 'ET':
    band = 'ET_500m'
  elif band == 'Le' or band == 'LE':
    band = 'LE_500m'
  else:    raise ValueError("Band must be either 'ET' or 'Le'")

  chunks = split_into_chunks(start_date, end_date)
  async with httpx.AsyncClient() as client:
    tasks = [
      fetch_modis(client, band, lat, lon, start_date, end_date) ## monta a url para cada chunk e faz a requisição
      for start_date, end_date in chunks
    ]
    responses = await asyncio.gather(*tasks)

  data = merge_responses(list(responses), start_date, end_date, band) ## junta as respostas dos chunks em uma única resposta

  folder = "outputs"
  if not os.path.exists(folder):
    os.makedirs(folder)

  file_path = os.path.join(folder, f"modis_{band}_{lat}_{lon}_{start_date}_{end_date}.json")
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

  return data
