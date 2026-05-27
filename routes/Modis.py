from fastapi import APIRouter, HTTPException

from scripts.Et_Le import get_modis
from schemas.Et_Le import modisRequest

router = APIRouter()

@router.get("/VegInd-BioFlux")
async def get_modis_params(band: str = 'ET', lat: float = 39.7, lon: float = -8.1, start_date: str = '2025001', end_date: str = '2025365'):
    response = await get_modis(band, lat, lon, start_date, end_date)
    return response

@router.post("/teste")
async def post_modis_params(payload: modisRequest):
    if (payload.band not in ['ET', 'LE']):
        raise HTTPException(
            status_code=400,
            detail=f"bad request: band '{payload.band}' not supported. Supported bands are: 'ET' and 'LE'"
        )
    
    response = await get_modis(band=payload.band, lat=payload.lat, lon=payload.lon, start_date=payload.start_date, end_date=payload.end_date)
    return response
