import httpx
from datetime import datetime, timedelta

MODIS_MAX_TILES = 10
MODIS_TILE_DAYS = 8

def julian_to_date(julian: str) -> datetime:
    return datetime.strptime(julian, "%Y%j")
 
 
def date_to_julian(date: datetime) -> str:
    return date.strftime("%Y%j")

def split_into_chunks(start_date: str, end_date: str) -> list[tuple[str, str]]:
  
  ## converte as datas de julian para datetime para facilitar a manipulação
  start = julian_to_date(start_date) 
  end = julian_to_date(end_date)
  print(f"start: {start}, end: {end}")

  chunks = []
  chunk_start = start ## inicia o chunk no dia inicial da requisição

  while chunk_start < end:
    chunk_end = chunk_start + timedelta(days=MODIS_MAX_TILES * MODIS_TILE_DAYS - 1) ## Ex: 2025001 + 79 dias = 2025080 - o -1 é para contar o dia inicial como parte do chunk

    chunk_end = min(chunk_end, end) ## garante que o chunk_end não ultrapasse a data final
    chunks.append((date_to_julian(chunk_start), date_to_julian(chunk_end))) ## Ex: (2025001, 2025009), (2025010, 2025018) ...

    chunk_start = chunk_end + timedelta(days=1) ## proximo dia após o final do chunk atual - Ex: 2025009 para 2025010

  return chunks

## Cria a url para cada chunk e faz a requisição para cada um deles
async def fetch_modis(client: httpx.AsyncClient, band: str, lat: float, lon: float, start: str, end: str) -> dict:
  url = (
        f"https://modis.ornl.gov/rst/api/v1/MOD16A2/subset?"
        f"latitude={lat}&longitude={lon}"
        f"&startDate=A{start}&endDate=A{end}"
        f"&product=MOD16A2&band={band}"
        f"&kmAboveBelow=5&kmLeftRight=5"
    )
  
  response = await client.get(url, timeout=60.0)
  return response.json()

## Junta as respostas de cada chunk em uma única resposta, garantindo que a estrutura do JSON seja mantida e que os dados sejam combinados corretamente
def merge_responses(responses: list[dict], start_date: str, end_date: str, band: str) -> dict:
  ## Verifica se a lista de respostas está vazia e retorna um dicionário vazio se for o caso
  if not responses:
    return {}
  
  merged = dict(responses[0]) ## Começa com a primeira resposta como base para o JSON final, garantindo que a estrutura seja mantida. O header é atualizado para refletir o intervalo total de datas e o produto solicitado.
  merged["header"] = f"https://modisrest.ornl.gov/rst/api/v1/MOD16A2/subset?latitude=39.7&longitude=-8.1&startDate=A{start_date}&endDate=A{end_date}&product=MOD16A2&band={band}&kmAboveBelow=5&kmLeftRight=5",
  merged["subset"] = [] ## Inicializa a chave "subset" como uma lista vazia para armazenar os dados combinados de todos os chunks

  for response in responses:
    subset = response.get("subset", []) ## Extrai a lista de dados do chunk atual usando get para evitar erros caso a chave "subset" não exista
    merged["subset"].extend(subset) ## Adiciona os dados do chunk atual à lista "subset" do JSON final usando extend para combinar as listas

  return merged 
