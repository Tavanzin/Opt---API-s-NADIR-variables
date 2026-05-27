# **Copernicus & Modis API**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-4B0082)](https://www.uvicorn.org/)
[![Scalar](https://img.shields.io/badge/ScalaDocs-3949AB?logo=scalar&logoColor=white)](https://scalar.com)
[![Copernicus Data Space](https://img.shields.io/badge/Copernicus-cdse-darkblue)](https://dataspace.copernicus.eu)
[![Modis](https://img.shields.io/badge/Modis-Et|Le-8B4513?logo=nasa&logoColor=white)](https://modis.ornl.gov/)
[![SentinelHub](https://img.shields.io/badge/SentinelHub-Scripts-73A724)](https://docs.sentinel-hub.com/api/latest/)
> Sentinel Hub fornece os scripts para os dados da **Copernicus(cdse)**

API em Python com FastAPI para consulta de dados de satélite — índices de vegetação, evapotranspiração e elevação de terreno sobre Portugal (e áreas configuráveis).

---

## Estrutura do Projeto

```
.
├── main.py                        # Ponto de entrada da aplicação
├── auth/
│   └── CopernicusAuth.py          # Autenticação OAuth Copernicus
├── controllers/
│   ├── CopernicusController.py    # Lógica de coordenadas e intervalos de datas
│   └── ModisController.py         # Lógica das datas e criação da url e request
├── routes/
│   ├── Copernicus.py              # Rotas NDVI, FAPAR, LAI, DEM
│   └── Modis.py                   # Rotas MODIS (evapotranspiração)
├── scripts/
│   ├── ndvi.py                    # Cálculo NDVI via Sentinel-2
│   ├── fapar.py                   # Cálculo FAPAR via Sentinel-2
│   ├── lai.py                     # Cálculo LAI via Sentinel-2
│   ├── dem.py                     # Download DEM Copernicus 30m
│   └── modis.py                   # Consulta MODIS MOD16A2
├── schemas/
│   ├── CoperniscusScema.py
│   └── Et_Le.py
└── Testes/
    └── teste.py
```

---

## Credenciais

No arquivo `.env` preencher as credenciais da API da **Copernicus**:

```python
CLIENT_ID = "o-teu-client-id"
CLIENT_SECRET = "o-teu-client-secret"
```

---


## Para correr com uvicorn

```bash
uvicorn main:app --reload
```

---

# Usar a API

## Endpoints

```
.
├── Copernicus              # Prefixo dos dados da Copernicus 
│   ├── /ndvi               # GET que pede o NDVI
│   ├── /fapar              # GET que pede o fapar
│   ├── /lai                # GET que pede o lai
│   ├── /dem                # GET que pede o dem não pede data
│   └── /teste              # Único metodo POST. Permite pedir todos as variaveis dos endpoint anteriores
└── Modis                   # Prefixo para os dados da Modis
    ├── /VegInd-BioFlux     # Get para Evapotranspiration e Latent heat flux
    └── /teste              # POST Permite pedir as duas variaveis através do payload
```

---

## **Respostas**

### Copernicus

### `GET`

#### `GET /Copernicus/ndvi | fapar | lai`

Retorna a variável pedida calculando com bands de acordo com os scripts fornecidos pela [SentinelHub](https://docs.sentinel-hub.com/api/latest/).
A resposta vem em um ficheiro `.zip` com os GeoTIFFs. (O pedido é dividio em quatro quadrantes)

**Parâmetros (opcionais):**

| Parâmetro    | Tipo   | Default     | Descrição                          |
|--------------|--------|-------------|-------------------------------------|
| `north`      | float  | `42.3`      | Latitude norte da bounding box      |
| `south`      | float  | `36.8`      | Latitude sul da bounding box        |
| `west`       | float  | `-9.7`      | Longitude oeste da bounding box     |
| `east`       | float  | `-6.1`      | Longitude este da bounding box      |
| `start_date` | string | `2025-01`   | Mês de início no formato `YYYY-MM`  |
| `end_date`   | string | `2025-12`   | Mês de fim no formato `YYYY-MM`     |

**Resposta:** `application/zip` com GeoTIFFs nomeados `{quadrante}_{mês}_ndvi.tiff`

---

#### `GET /Copernicus/dem`

Retorna um GeoTIFF com o Modelo Digital de Elevação (DEM Copernicus 30m) para Portugal Continental.

| Parâmetro    | Tipo   | Default     | Descrição                          |
|--------------|--------|-------------|-------------------------------------|
| `north`      | float  | `42.3`      | Latitude norte da bounding box      |
| `south`      | float  | `36.8`      | Latitude sul da bounding box        |
| `west`       | float  | `-9.7`      | Longitude oeste da bounding box     |
| `east`       | float  | `-6.1`      | Longitude este da bounding box      |

**Resposta:** `image/tiff`

---

### `POST`

#### `POST /Copernicus/teste``

Serve como uma alternativa, permite pedir todas as variáveis que se pede com os `GET's` mas envia os pedidos através do **JSON no corpo do request**.

- `schemas/CopernicusSchema.py`

**Body (JSON):**

| Campo        | Tipo        | Default                     | Descrição                                           |
|--------------|-------------|-----------------------------|-----------------------------------------------------|
| `variable`   | string      | `"ndvi"`                    | Variável a consultar: `ndvi`, `fapar`, `lai`, `dem` |
| `bbox`       | list[float] | `[42.3, 36.8, -9.7, -6.1]` | Bounding box: `[north, south, west, east]`          |
| `start_date` | string      | `"2025-01"`                 | Mês de início no formato `YYYY-MM`                  |
| `end_date`   | string      | `"2025-12"`                 | Mês de fim no formato `YYYY-MM`                     |

**Exemplo de request:**

```json
{
  "variable": "ndvi",
  "bbox": [42.3, 36.8, -9.7, -6.1],
  "start_date": "2025-01",
  "end_date": "2025-03"
}
```

**Resposta:**

- Se `variable` for `ndvi`, `fapar` ou `lai`: `application/zip` com GeoTIFFs nomeados `{quadrante}_{mês}_{variável}.tiff`
- Se `variable` for `dem`: `image/tiff` diretamente
- Se `variable` não for suportada ou o **json** estiver mal formatdo: `400 Bad Request`

---

### `GET`

#### `GET /Modis/VegInd-BioFlux`

Retorna dados sobre o indície de vegetação (Evapotranspiração [Et]) e fluxo bioquímico (Fluxo de calor latente [Le]) de um ponto específico com uma área ao envolta de no máximo 100x100km

| Parâmetro    | Tipo   | Default     | Descrição                                    |
|--------------|--------|-------------|-----------------------------------------------|
| `band`       | string | `ET`        | Banda do produto MODIS a consultar          |
| `lat`        | float  | `39.7`      | Latitude do ponto                             |
| `lon`        | float  | `-8.1`      | Longitude do ponto                            |
| `start_date` | string | `2025001`   | Data de início em formato juliano (`YYYYDDD`) |
| `end_date`   | string | `2025365`   | Data de fim em formato juliano (`YYYYDDD`)    |

> As datas tem formato juliano(`yyyyddd`): 2025001 = 01-01-2025

O pedido é divido em `chunks` cada chunk é um perído de **80 dias (10 tiles)**

---

### `POST`

#### `POST Modis/teste`

Também é uma alternativa para o `GET` mas não muda pois as duas variáveis estão em um só endpoint

- `schemas/Et_Le.py`

**Body (JSON):**

| Campo        | Tipo   | Default     | Descrição                                                     |
|--------------|--------|-------------|---------------------------------------------------------------|
| `band`       | string | `"ET"`      | Banda MODIS: `ET` (evapotranspiração) ou `LE` (calor latente) |
| `lat`        | float  | `39.7`      | Latitude do ponto                                             |
| `lon`        | float  | `-8.1`      | Longitude do ponto                                            |
| `start_date` | string | `"2025001"` | Data de início em formato juliano `YYYYDDD`                   |
| `end_date`   | string | `"2025365"` | Data de fim em formato juliano `YYYYDDD`                      |

**Exemplo de request:**

```json
{
  "band": "LE",
  "lat": 38.7,
  "lon": -9.1,
  "start_date": "2025001",
  "end_date": "2025365"
}
```

**Resposta:** JSON com os dados MODIS agregados para o intervalo completo.

> Se o pedido exceder os **80 dias (10 tile)** os chunks são feitos sozinhos em paralelo

---

## Autenticação
 
### `auth/CopernicusAuth.py`
 
Responsável por obter o **bearer token** da API Copernicus antes de cada pedido. Usa as credenciais definidas no `.env` para fazer o pedido de autenticação OAuth2 com `client_credentials`.
 
#### `get_Copernicus_accessToken() -> str`
 
| | |
|---|---|
| **Tipo** | `async` |
| **Retorna** | `str` — o access token para usar no header `Authorization: Bearer <token>` |
 
**Como funciona:**
 
1. Lê `COPERNICUS_CLIENT_ID` e `COPERNICUS_CLIENT_SECRET` do `.env` via `os.getenv()`
2. Faz um `POST` ao endpoint de autenticação da Copernicus com `grant_type: client_credentials`
3. Extrai e devolve o `access_token` da resposta JSON
> O token é pedido a cada request — não é guardado em cache. Se quiseres otimizar, podes guardar o token e renová-lo apenas quando expirar.

---

## **Funções (Controllers)**

Os controller tem as lógicas de apoio para montar url`s, tratar coordenadas e intervalo de datas antes de irem para os scripts.

### `CopernicusController.py`

#### `get_bbox(n, s, w, e) -> list`

Constrói a lista de coordenadas que define o polígono de uma bounding box.
 
| Parâmetro | Tipo  | Descrição       |
|-----------|-------|-----------------|
| `n`       | float | Latitude norte  |
| `s`       | float | Latitude sul    |
| `w`       | float | Longitude oeste |
| `e`       | float | Longitude este  |

**Retorna:** lista de 5 pares `[lon, lat]` que formam o polígono fechado (o último ponto repete o primeiro).
 
```
[w,n] → [e,n] → [e,s] → [w,s] → [w,n]
```
 
> Usada internamente por `get_coordinates` — não é chamada diretamente pelas rotas.

---

#### `get_coordinates(north, south, west, east) -> dict`
 
Divide a bounding box pedida em **4 quadrantes** e devolve as coordenadas de cada um.
 
| Parâmetro | Tipo  | Descrição                     |
|-----------|-------|-------------------------------|
| `north`   | float | Latitude norte da área total  |
| `south`   | float | Latitude sul da área total    |
| `west`    | float | Longitude oeste da área total |
| `east`    | float | Longitude este da área total  |
 
**Retorna:** `dict` com 4 entradas, cada uma com a bounding box do respetivo quadrante:
 
```python
{
    "noroeste": [...],
    "nordeste":  [...],
    "sudoeste":  [...],
    "sudeste":   [...]
}
```
 
> A divisão é feita pelo ponto médio (`mid_lat`, `mid_lon`). É necessária porque a API Copernicus tem um limite de área por request.

---

#### `get_months_interval(start_date, end_date) -> list[str]`
 
Gera a lista de todos os meses entre duas datas, inclusive os extremos.
 
| Parâmetro    | Tipo | Formato   | Exemplo     |
|--------------|------|-----------|-------------|
| `start_date` | str  | `YYYY-MM` | `"2025-01"` |
| `end_date`   | str  | `YYYY-MM` | `"2025-04"` |
 
**Retorna:** `list[str]` com todos os meses no intervalo:
 
```python
get_months_interval("2025-01", "2025-04")
# → ["2025-01", "2025-02", "2025-03", "2025-04"]
```
 
> Usada pelas rotas Copernicus para iterar mês a mês e gerar uma task por quadrante por mês.
 
---

#### `add_month(date) -> str`
 
Adiciona um mês a uma data.
 
| Parâmetro | Tipo | Formato   | Exemplo     |
|-----------|------|-----------|-------------|
| `date`    | str  | `YYYY-MM` | `"2025-12"` |
 
**Retorna:** `str` com o mês seguinte no mesmo formato:
 
```python
add_month("2025-12")  # → "2026-01"
add_month("2025-06")  # → "2025-07"
```
 
> Usa `relativedelta` do `python-dateutil` para tratar corretamente a transição de ano (Dezembro → Janeiro).

--- 

### `ModisController.py`
 
---
 
#### `julian_to_date(julian: str) -> datetime` & `date_to_julian(date: datetime) -> str`
 
Par de funções inversas que convertem entre o formato juliano (`YYYYDDD`) e `datetime`, para facilitar a aritmética de datas.
 
| Função | Entrada | Saída |
|---|---|---|
| `julian_to_date` | `"2025032"` | `datetime(2025, 2, 1)` |
| `date_to_julian` | `datetime(2025, 2, 1)` | `"2025032"` |
 
> Usadas internamente por `split_into_chunks` — a API exige formato juliano, mas somar dias é mais simples com `datetime`.
 
---
 
#### `split_into_chunks(start_date: str, end_date: str) -> list[tuple[str, str]]`
 
Parte o intervalo de datas em chunks de no máximo **80 dias (10 tiles × 8 dias)**, que é o limite da API MODIS por request.
 
| Parâmetro    | Tipo | Formato   | Descrição      |
|--------------|------|-----------|----------------|
| `start_date` | str  | `YYYYDDD` | Data de início |
| `end_date`   | str  | `YYYYDDD` | Data de fim    |
 
**Retorna:** `list[tuple[str, str]]` — lista de pares `(início, fim)` em formato juliano:
 
```python
split_into_chunks("2025001", "2025200")
# → [("2025001", "2025080"), ("2025081", "2025160"), ("2025161", "2025200")]
```
 
**Como funciona:**
- `chunk_end = chunk_start + 79 dias` — o `-1` garante que o dia inicial conta como parte do chunk
- `min(chunk_end, end)` — garante que o último chunk não ultrapassa a data final pedida
- O próximo chunk começa no dia seguinte ao fim do chunk atual (`chunk_end + 1 dia`)
---
 
#### `fetch_modis(client, band, lat, lon, start, end) -> dict`
 
Constrói a URL e faz um único request à API MODIS para um chunk.
 
| Parâmetro | Tipo                | Descrição                                     |
|-----------|---------------------|-----------------------------------------------|
| `client`  | `httpx.AsyncClient` | Cliente HTTP partilhado entre todos os chunks |
| `band`    | str                 | Banda MODIS: `ET` ou `LE`                     |
| `lat`     | float               | Latitude do ponto                             |
| `lon`     | float               | Longitude do ponto                            |
| `start`   | str                 | Data de início do chunk em formato juliano    |
| `end`     | str                 | Data de fim do chunk em formato juliano       |
 
**Retorna:** `dict` com a resposta JSON da API para aquele chunk.
 
> O `client` é recebido como parâmetro em vez de criado dentro da função para reutilizar a mesma ligação TCP em todos os chunks — mais eficiente do que abrir e fechar uma ligação por cada request.
 
---
 
#### `merge_responses(responses, start_date, end_date, band) -> dict`
 
Agrega as respostas de todos os chunks numa única resposta final, mantendo a estrutura JSON da API MODIS.
 
| Parâmetro    | Tipo       | Descrição                                        |
|--------------|------------|--------------------------------------------------|
| `responses`  | list[dict] | Lista de respostas de cada chunk                 |
| `start_date` | str        | Data de início total (para reconstruir o header) |
| `end_date`   | str        | Data de fim total (para reconstruir o header)    |
| `band`       | str        | Banda pedida (para reconstruir o header)         |
 
**Retorna:** `dict` com a estrutura completa — metadados do primeiro chunk com todos os `subset` concatenados.
 
**O que faz:**
- Usa o primeiro response como base (tem os metadados: lat, lon, unidade, etc.)
- Reconstrói o `header` com o intervalo **total** em vez do intervalo do primeiro chunk
- Usa `.extend()` (não `.append()`) para manter a lista `subset` plana:
```python
merged["subset"].append(subset)  # → [[...], [...]]  lista de listas
merged["subset"].extend(subset)  # → [..., ...]      lista plana
```
 
> Se `responses` for uma lista vazia, devolve `{}` imediatamente.
