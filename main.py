from fastapi import FastAPI, APIRouter
from routes import Copernicus, Modis
from scalar_fastapi import get_scalar_api_reference

tags_metadata = [
    {
        "name": "Copernicus",
        "description": """
Endpoints para consulta de dados **Copernicus/Sentinel-2**.

Todos devolvem ficheiros `.zip` com GeoTIFFs, um por quadrante por mês.
A área é automaticamente dividida em 4 quadrantes (NW, NE, SW, SE).
        """,
    },
    {
        "name": "MODIS",
        "description": """
Endpoints para consulta de **evapotranspiração** e **latent heat flux** (produto MOD16A2).

Suporta intervalos superiores a 80 dias — os pedidos são partidos em chunks automaticamente.
        """,
    },
]


app = FastAPI(
    title="API NADIR (Copernicus & Modis)",
    description="API para consulta de dados de satélite do Copernicus e MODIS, com endpoints dedicados para cada um.",
    openapi_tags=tags_metadata
)
router = APIRouter()


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        # Your OpenAPI document
        openapi_url=app.openapi_url,
        # Avoid CORS issues (optional)
        scalar_proxy_url="https://proxy.scalar.com",
    )

app.include_router(Copernicus.router, prefix='/Copernicus', tags=["Copernicus"])
app.include_router(Modis.router, prefix='/Modis', tags=["Modis"])
