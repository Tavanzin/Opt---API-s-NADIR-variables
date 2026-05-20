# Copernicus & MODIS API

API em Python com FastAPI para consulta de dados de satélite — índices de vegetação, evapotranspiração e elevação de terreno sobre Portugal.

---

## Pré-requisitos

- Python 3.10+
- Conta na [Copernicus Data Space](https://dataspace.copernicus.eu/) (para NDVI, FAPAR, LAI, DEM)

## Credenciais

Edita os ficheiros abaixo com as tuas credenciais antes de correr o projeto:

**`auth.py`** — credenciais da API Copernicus:
```python
CLIENT_ID = "o-teu-client-id"
CLIENT_SECRET = "o-teu-client-secret"
```

**`modisDownload.py`** — credenciais NASA Earthdata:
```python
USERNAME = "o-teu-username"
PASSWORD = "a-tua-password"
```

## Endpoints

### `GET /ndvi`
Retorna o NDVI (Índice de Vegetação por Diferença Normalizada) por quadrante, calculado com bandas Sentinel-2.

**Parâmetros (opcionais):**
| Parâmetro | Tipo | Default |
|-----------|------|---------|
| north | float | 42.3 |
| south | float | 36.8 |
| west | float | -9.7 |
| east | float | -6.1 |

---

### `GET /fapar`
Retorna o FAPAR (Fração de Radiação Fotossinteticamente Ativa Absorvida) por quadrante, usando rede neural aplicada sobre Sentinel-2.

Aceita os mesmos parâmetros de bounding box que `/ndvi`.

---

### `GET /Lai`
Retorna o LAI (Índice de Área Foliar) por quadrante, usando rede neural aplicada sobre Sentinel-2.

Aceita os mesmos parâmetros de bounding box que `/ndvi`.

---

### `GET /dem`
Retorna uma imagem GeoTIFF com o Modelo Digital de Elevação (DEM Copernicus 30m) para Portugal.

Não aceita parâmetros — a bbox está fixa em Portugal Continental.

---

### `GET /modis/data`
Retorna dados de evapotranspiração do produto MODIS MOD16A2 para um ponto específico.

**Parâmetros (opcionais):**
| Parâmetro | Tipo | Default | Exemplo |
|-----------|------|---------|---------|
| band | str | ET_500m | ET_500m, LE_500m |
| lat | float | 39.7 | — |
| lon | float | -8.1 | — |
| start_date | str | 2025001 | 2025001 (dia juliano) |
| end_date | str | 2025009 | — |

---

## Notas

- A divisão em quadrantes existe porque a API Copernicus tem limite de área por pedido.
- As datas do MODIS usam o formato juliano (`YYYYDDD`), ex: `2025001` = 1 de janeiro de 2025.
