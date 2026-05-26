# Copernicus & MODIS API

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

## Pré-requisitos

- Python 3.10+
- Conta na [Copernicus Data Space](https://dataspace.copernicus.eu/) (para NDVI, FAPAR, LAI, DEM)

## Credenciais

Antes de correr o projeto, preenche as credenciais nos ficheiros abaixo:

**`auth/CopernicusAuth.py`** — credenciais da API Copernicus:
```python
CLIENT_ID = "o-teu-client-id"
CLIENT_SECRET = "o-teu-client-secret"
```

---

## Como Correr

```bash
uvicorn main:app --reload
```

---

## Endpoints

Todos os endpoints Copernicus estão sob o prefixo `/Copernicus` e os MODIS sob `/Modis`.

---

### `GET /Copernicus/ndvi`

Retorna o NDVI (Índice de Vegetação por Diferença Normalizada) calculado com bandas Sentinel-2, por quadrante e por mês. A resposta é um ficheiro `.zip` contendo GeoTIFFs.

**Parâmetros (opcionais):**

| Parâmetro    | Tipo   | Default     | Descrição                          |
|--------------|--------|-------------|-------------------------------------|
| `north`      | float  | `42.3`      | Latitude norte da bounding box      |
| `south`      | float  | `36.8`      | Latitude sul da bounding box        |
| `west`       | float  | `-9.7`      | Longitude oeste da bounding box     |
| `east`       | float  | `-6.1`      | Longitude este da bounding box      |
| `start_date` | string | `2025-01`   | Mês de início no formato `YYYY-MM`  |
| `end_date`   | string | `2025-01`   | Mês de fim no formato `YYYY-MM`     |

**Resposta:** `application/zip` com GeoTIFFs nomeados `{quadrante}_{mês}_ndvi.tiff`

---

### `GET /Copernicus/fapar`

Retorna o FAPAR (Fração de Radiação Fotossinteticamente Ativa Absorvida), calculado via rede neural sobre Sentinel-2, por quadrante e por mês.

Aceita os mesmos parâmetros que `/Copernicus/ndvi`.

**Resposta:** `application/zip` com GeoTIFFs nomeados `{quadrante}_{mês}_fapar.tiff`

---

### `GET /Copernicus/lai`

Retorna o LAI (Índice de Área Foliar), calculado via rede neural sobre Sentinel-2, por quadrante e por mês.

Aceita os mesmos parâmetros que `/Copernicus/ndvi`.

**Resposta:** `application/zip` com GeoTIFFs nomeados `{quadrante}_{mês}_lai.tiff`

---

### `GET /Copernicus/dem`

Retorna um GeoTIFF com o Modelo Digital de Elevação (DEM Copernicus 30m) para Portugal Continental.

| Parâmetro    | Tipo   | Default     | Descrição                          |
|--------------|--------|-------------|-------------------------------------|
| `north`      | float  | `42.3`      | Latitude norte da bounding box      |
| `south`      | float  | `36.8`      | Latitude sul da bounding box        |
| `west`       | float  | `-9.7`      | Longitude oeste da bounding box     |
| `east`       | float  | `-6.1`      | Longitude este da bounding box      |

> Não precisa de datas pois a altura não muda com o tempo

**Resposta:** `image/tiff`

---

### `GET /Modis`

Retorna dados de evapotranspiração do produto MODIS MOD16A2 para um ponto específico.

**Parâmetros (opcionais):**

| Parâmetro    | Tipo   | Default     | Exemplo            | Descrição                                    |
|--------------|--------|-------------|--------------------|-----------------------------------------------|
| `band`       | string | `ET`         | `ET`, `LE`          | Banda do produto MODIS a consultar          |
| `lat`        | float  | `39.7`      | `38.7`             | Latitude do ponto                             |
| `lon`        | float  | `-8.1`      | `-9.1`             | Longitude do ponto                            |
| `start_date` | string | `2025001`   | `2025001`          | Data de início em formato juliano (`YYYYDDD`) |
| `end_date`   | string | `2025009`   | `2025009`          | Data de fim em formato juliano (`YYYYDDD`)    |

> As datas usam o formato juliano: `2025001` = 1 de Janeiro de 2025, `2025032` = 1 de Fevereiro de 2025.

### Limite de tiles & Chunking automático

A API MODIS limita cada request a **10 tiles (80 dias)**.  
Se pedires mais, o sistema divide automaticamente e agrega tudo.

---

## POST Endpoints

Os endpoints `POST /teste` são versões alternativas dos `GET` que aceitam os parâmetros via **JSON no corpo do request** em vez de query string. Útil para clientes que preferem enviar body JSON (ex: Postman, aplicações frontend).

---

### `POST /Copernicus/teste`

Endpoint unificado que aceita qualquer variável Copernicus num único request. Em vez de ter rotas separadas para NDVI, FAPAR, LAI e DEM, escolhes a variável no campo `variable`.

**Body (JSON):**

| Campo        | Tipo        | Default                     | Descrição                                           |
|--------------|-------------|-----------------------------|-----------------------------------------------------|
| `variable`   | string      | `"ndvi"`                    | Variável a consultar: `ndvi`, `fapar`, `lai`, `dem` |
| `bbox`       | list[float] | `[42.3, 36.8, -9.7, -6.1]` | Bounding box: `[north, south, west, east]`          |
| `start_date` | string      | `"2025-01"`                 | Mês de início no formato `YYYY-MM`                  |
| `end_date`   | string      | `"2025-02"`                 | Mês de fim no formato `YYYY-MM`                     |

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
- Se `variable` não for suportada: `400 Bad Request`

---

### `POST /Modis/teste`

Versão POST do `GET /Modis`. Aceita os mesmos parâmetros via JSON. O chunking automático aplica-se da mesma forma.

**Body (JSON):**

| Campo        | Tipo   | Default     | Descrição                                                     |
|--------------|--------|-------------|---------------------------------------------------------------|
| `band`       | string | `"ET"`      | Banda MODIS: `ET` (evapotranspiração) ou `LE` (calor latente) |
| `lat`        | float  | `39.7`      | Latitude do ponto                                             |
| `lon`        | float  | `-8.1`      | Longitude do ponto                                            |
| `start_date` | string | `"2025001"` | Data de início em formato juliano `YYYYDDD`                   |
| `end_date`   | string | `"2025087"` | Data de fim em formato juliano `YYYYDDD`                      |

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

> Se o intervalo exceder 80 dias, os chunks são feitos automaticamente em paralelo — ver secção [Limite de tiles & Chunking automático](#limite-de-tiles--chunking-automático).

---

## Notas Técnicas

- **Divisão em quadrantes:** A área de interesse é automaticamente dividida em 4 quadrantes (noroeste, nordeste, sudoeste, sudeste) porque a API Copernicus tem um limite de área por pedido. Os resultados são agregados num único `.zip`.
- **Intervalo de meses:** Os endpoints Copernicus aceitam um intervalo `start_date`/`end_date` e geram um ficheiro por quadrante por mês dentro desse intervalo.
- **Formato de datas Copernicus:** `YYYY-MM` (ex: `2025-03`)
- **Formato de datas MODIS:** juliano `YYYYDDD` (ex: `2025060` = 1 de Março de 2025)
