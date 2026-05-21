from fastapi import APIRouter

from scripts.Et_Le import get_modis

router = APIRouter()

@router.get("")
async def get_params(band: str = 'ET', lat: float = 39.7, lon: float = -8.1, start_date: str = '2025001', end_date: str = '2025087'):
    response = await get_modis(band, lat, lon, start_date, end_date)
    return response
