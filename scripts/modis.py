import httpx
import json
import os
import asyncio

from controllers.ModisController import fetch_modis, merge_responses, split_into_chunks

async def get_modis(band: str, lat: float, lon: float, start_date: str, end_date: str) -> dict:
  ## O serviço MODIS tem um limite de 10 tiles por requisição, e cada tile cobre um período de 8 dias. 
  # Para garantir que a requisição seja bem-sucedida, é necessário dividir o intervalo total de datas em chunks menores que respeitem esse limite.
  chunks = split_into_chunks(start_date, end_date)
  async with httpx.AsyncClient() as client:
    tasks = [
      fetch_modis(client, band, lat, lon, start_date, end_date) ## monta a url para cada chunk e faz a requisição
      for start_date, end_date in chunks
    ]
    responses = await asyncio.gather(*tasks)

  data = merge_responses(list(responses), start_date, end_date, band)

  folder = "outputs"
  if not os.path.exists(folder):
    os.makedirs(folder)

  file_path = os.path.join(folder, f"modis_{band}_{lat}_{lon}_{start_date}_{end_date}.json")
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

  return data
