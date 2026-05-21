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
│   └── CopernicusController.py    # Lógica de coordenadas e intervalos de datas
├── routes/
│   ├── Copernicus.py              # Rotas NDVI, FAPAR, LAI, DEM
│   └── Modis.py                   # Rotas MODIS (evapotranspiração)
├── scripts/
│   ├── ndvi.py                    # Cálculo NDVI via Sentinel-2
│   ├── fapar.py                   # Cálculo FAPAR via Sentinel-2
│   ├── lai.py                     # Cálculo LAI via Sentinel-2
│   ├── dem.py                     # Download DEM Copernicus 30m
│   └── modis.py                   # Consulta MODIS MOD16A2
└── Testes/
    └── teste.py
```

---

## Pré-requisitos

- Python 3.10+
- Conta na [Copernicus Data Space](https://dataspace.copernicus.eu/) (para NDVI, FAPAR, LAI, DEM)
- Conta na [NASA Earthdata](https://urs.earthdata.nasa.gov/) (para MODIS)

### Instalar dependências

```bash
pip install fastapi uvicorn python-dateutil
```

---

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

A API ficará disponível em `http://localhost:8000`.  
Documentação automática em `http://localhost:8000/docs`.

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
| `band`       | string | `ET_500m`   | `ET_500m`, `LE_500m` | Banda do produto MODIS a consultar          |
| `lat`        | float  | `39.7`      | `38.7`             | Latitude do ponto                             |
| `lon`        | float  | `-8.1`      | `-9.1`             | Longitude do ponto                            |
| `start_date` | string | `2025001`   | `2025001`          | Data de início em formato juliano (`YYYYDDD`) |
| `end_date`   | string | `2025009`   | `2025009`          | Data de fim em formato juliano (`YYYYDDD`)    |

> As datas usam o formato juliano: `2025001` = 1 de Janeiro de 2025, `2025032` = 1 de Fevereiro de 2025.


### Limite de tiles & Chunking automático

A API MODIS limita cada request a **10 tiles (80 dias)**.  
Se pedires mais, o sistema divide automaticamente e agrega tudo.

---

## Notas Técnicas

- **Divisão em quadrantes:** A área de interesse é automaticamente dividida em 4 quadrantes (noroeste, nordeste, sudoeste, sudeste) porque a API Copernicus tem um limite de área por pedido. Os resultados são agregados num único `.zip`.
- **Intervalo de meses:** Os endpoints Copernicus aceitam um intervalo `start_date`/`end_date` e geram um ficheiro por quadrante por mês dentro desse intervalo.
- **Formato de datas Copernicus:** `YYYY-MM` (ex: `2025-03`)
- **Formato de datas MODIS:** juliano `YYYYDDD` (ex: `2025060` = 1 de Março de 2025)
