from fastapi import APIRouter

from scripts.modis import get_modis

router = APIRouter()

@router.get("")
async def get_params(band: str = 'ET_500m', lat: float = 39.7, lon: float = -8.1, start_date: str = '2025001', end_date: str = '2025009'):
    response = await get_modis(band, lat, lon, start_date, end_date)
    return response
