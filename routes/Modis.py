from fastapi import APIRouter
from rasterio import band

from scripts.Et_Le import get_modis
from schemas.Et_Le import modisRequest

router = APIRouter()

@router.get("")
async def get_modis_params(band: str = 'ET', lat: float = 39.7, lon: float = -8.1, start_date: str = '2025001', end_date: str = '2025087'):
    response = await get_modis(band, lat, lon, start_date, end_date)
    return response

@router.post("/teste")
async def post_modis_params(payload: modisRequest):
    response = await get_modis(band=payload.band, lat=payload.lat, lon=payload.lon, start_date=payload.start_date, end_date=payload.end_date)
    return response
