from fastapi import APIRouter, HTTPException

from scripts.Et_Le import get_modis
from schemas.Et_Le import modisRequest
from datetime import datetime

router = APIRouter()

@router.get("/VegInd-BioFlux", 
            responses={400: {"description": "Bad Request"}}
            )
async def get_modis_params(band: str = 'ET', lat: float = 39.7, lon: float = -8.1, start_date: str = '2025001', end_date: str = '2025365'):
    if (band not in ['ET', 'LE']):
        raise HTTPException(
            status_code=400,
            detail=f"bad request: band '{band}' not supported. Supported bands are: 'ET' and 'LE'"
        )
    
    try:  
        data_inicio = datetime.strptime(start_date, "%Y%j").date()
        data_fim = datetime.strptime(end_date, "%Y%j").date()

        if (data_inicio > data_fim or 
            data_inicio > datetime.today().date() or 
            data_fim > datetime.today().date()):
            raise HTTPException(status_code=400)
    except ValueError:
        raise HTTPException(status_code=400)

    response = await get_modis(band, lat, lon, start_date, end_date)
    return response

@router.post("/teste", 
             responses={400: {"description": "Bad Request"}}
             )
async def post_modis_params(payload: modisRequest):
    try:  
        data_inicio = datetime.strptime(payload.start_date, "%Y%j").date()
        data_fim = datetime.strptime(payload.end_date, "%Y%j").date()

        if (data_inicio > data_fim or 
            data_inicio > datetime.today().date() or 
            data_fim > datetime.today().date()):
            raise HTTPException(status_code=400)
    except ValueError:
        raise HTTPException(status_code=400)

    if (payload.band not in ['ET', 'LE']):
        raise HTTPException(
            status_code=400,
            detail=f"bad request: band '{payload.band}' not supported. Supported bands are: 'ET' and 'LE'"
        )
    
    response = await get_modis(band=payload.band, lat=payload.lat, lon=payload.lon, start_date=payload.start_date, end_date=payload.end_date)
    return response
