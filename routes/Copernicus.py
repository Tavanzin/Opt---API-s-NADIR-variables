from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from datetime import datetime, date
import io
import zipfile

from controllers.CopernicusController import get_months_interval, get_coordinates

from scripts.ndvi import post_ndvi
from scripts.fapar import post_fapar
from scripts.lai import post_lai
from scripts.dem import post_dem
from schemas.CopernicusSchema import Copernicus

import asyncio

router = APIRouter()

@router.get("/ndvi", 
              responses={400: {"description": "Bad Request"}}
            )
async def get_ndvi(north: float = 42.3, south: float = 36.8,
                    west: float = -9.7, east: float = -6.1,
                    start_date :str = '2025-01', end_date :str = '2025-12'
                    ):
  try:  
    data_inicio = datetime.strptime(start_date, "%Y-%m").date()
    data_fim = datetime.strptime(end_date, "%Y-%m").date()

    if (start_date > end_date or 
        data_inicio > date.today() or 
        data_fim > date.today()  or
        data_inicio.month < 1 or data_inicio.month > 12 or
        data_fim.month < 1 or data_fim.month > 12):
      raise HTTPException(status_code=400)
  except ValueError:
    raise HTTPException(status_code=400)

  raw_coordinates = get_coordinates(north, south, west, east)
  names = list(raw_coordinates.keys())
  coords = list(raw_coordinates.values())

  months_interval = get_months_interval(start_date, end_date)

  tasks = []
  data = []

  for name, c in zip(names, coords):
      for month in months_interval:
          tasks.append(post_ndvi(c, start_date=month, end_date=month))

          data.append((name, month))


  responses = await asyncio.gather(*tasks)

  buffer = io.BytesIO()
  with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, tiff_bytes in zip(data, responses):
            zf.writestr(f"{name}_{month}_ndvi.tiff", tiff_bytes)
  buffer.seek(0)  

  return StreamingResponse(
    buffer,
    media_type="application/zip",
    headers={"Content-Disposition": f"attachment; filename={start_date}_{end_date}_ndvi.zip"}
  )

@router.get("/fapar",
            responses={400: {"description": "Bad Request"}}
            )
async def get_fapar(north: float = 42.3, south: float = 36.8,
                    west: float = -9.7, east: float = -6.1,
                    start_date :str = '2025-01', end_date :str = '2025-12'
                    ):
  try:
    data_inicio = datetime.strptime(start_date, "%Y-%m").date()
    data_fim = datetime.strptime(end_date, "%Y-%m").date()

    if (start_date > end_date or 
        data_inicio > date.today() or 
        data_fim > date.today()  or
        data_inicio.month < 1 or data_inicio.month > 12 or
        data_fim.month < 1 or data_fim.month > 12):
      raise HTTPException(status_code=400)
  except ValueError:
    raise HTTPException(status_code=400)

  raw_coordinates = get_coordinates(north, south, west, east)
  names = list(raw_coordinates.keys())
  coords = list(raw_coordinates.values())

  months_interval = get_months_interval(start_date, end_date)

  tasks = []
  data = []

  for name, c in zip(names, coords):
      for month in months_interval:
          tasks.append(post_fapar(c, start_date=month, end_date=month))

          data.append((name, month))

  responses = await asyncio.gather(*tasks)

  buffer = io.BytesIO()
  with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
      for name, tiff_bytes in zip(data, responses):
          zf.writestr(f"{name}_{month}_fapar.tiff", tiff_bytes)
  buffer.seek(0)

  return StreamingResponse(
    buffer,
    media_type="application/zip",
    headers={
        "Content-Disposition": f"attachment; filename={start_date}_{end_date}_fapar.zip"
    }
  )

@router.get("/lai",
             responses={400: {"description": "Bad Request"}}
            )
async def get_lai(north: float = 42.3, south: float = 36.8,
                    west: float = -9.7, east: float = -6.1,
                    start_date :str = '2025-01', end_date :str = '2025-12'
                    ):
    try:
      data_inicio = datetime.strptime(start_date, "%Y-%m").date()
      data_fim = datetime.strptime(end_date, "%Y-%m").date()

      if (start_date > end_date or 
          data_inicio > date.today() or 
          data_fim > date.today()  or
          data_inicio.month < 1 or data_inicio.month > 12 or
          data_fim.month < 1 or data_fim.month > 12):
        raise HTTPException(status_code=400)
    except ValueError:
      raise HTTPException(status_code=400)

    raw_coordinates = get_coordinates(north, south, west, east)
    names = list(raw_coordinates.keys())
    coords = list(raw_coordinates.values())

    months_interval = get_months_interval(start_date, end_date)

    tasks = []
    data = []

    for name, c in zip(names, coords):
      for month in months_interval:
          tasks.append(post_lai(c, start_date=month, end_date=month))

          data.append((name, month))

    responses = await asyncio.gather(*tasks)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, tiff_bytes in zip(data, responses):
            zf.writestr(f"{name}_{month}_lai.tiff", tiff_bytes)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={start_date}_{end_date}_lai.zip"
        }
    )

@router.get("/dem")
async def get_dem(north: float = 42.3, south: float = 36.8,
                    west: float = -9.7, east: float = -6.1):
   demTiff = await post_dem(north, south, west, east)
   return Response(content=demTiff, media_type="image/tiff", headers={"Content-Disposition": f"attachment; filename={north}_{south}_{west}_{east}_dem.tiff"})


### Endpoint de teste usando o modelo Copernicus para receber os parâmetros via JSON no corpo da requisição

@router.post("/teste",
             responses={400: {"description": "Bad Request"}}
             )
async def post_copernicus_params(payload: Copernicus):
    VARIAVEIS_SUPORTADAS = ['ndvi', 'fapar', 'lai', 'dem']

    try:
      data_inicio = datetime.strptime(payload.start_date, "%Y-%m").date()
      data_fim = datetime.strptime(payload.end_date, "%Y-%m").date()

      if payload.variable not in VARIAVEIS_SUPORTADAS:
        raise HTTPException(status_code=400, 
                            detail=f"bad request: variable '{payload.variable}' not supported. Supported variables are: {', '.join(VARIAVEIS_SUPORTADAS)}"
                            )
      
      if (payload.start_date > payload.end_date or
          data_inicio > date.today() or 
          data_fim > date.today()  or
          data_inicio.month < 1 or data_inicio.month > 12 or
          data_fim.month < 1 or data_fim.month > 12):
        raise HTTPException(status_code=400)
    except ValueError:
      raise HTTPException(status_code=400)

    if payload.variable == 'dem':
        demTiff = await post_dem(payload.bbox[0], payload.bbox[1], payload.bbox[2], payload.bbox[3])
        return Response(content=demTiff, media_type="image/tiff", headers={"Content-Disposition": f"attachment; filename={payload.bbox[0]}_{payload.bbox[1]}_{payload.bbox[2]}_{payload.bbox[3]}_dem.tiff"})
    
    raw_coordinates = get_coordinates(payload.bbox[0], payload.bbox[1], payload.bbox[2], payload.bbox[3])
    names = list(raw_coordinates.keys())
    coords = list(raw_coordinates.values())

    months_interval = get_months_interval(payload.start_date, payload.end_date)

    tasks = []
    data = []

    for name, c in zip(names, coords):
        for month in months_interval:
            if payload.variable == 'ndvi':
                tasks.append(post_ndvi(c, start_date=month, end_date=month))
            elif payload.variable == 'fapar':
                tasks.append(post_fapar(c, start_date=month, end_date=month))
            elif payload.variable == 'lai':
                tasks.append(post_lai(c, start_date=month, end_date=month))

            data.append((name, month))

    responses = await asyncio.gather(*tasks)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, tiff_bytes in zip(data, responses):
            zf.writestr(f"{name}_{month}_{payload.variable}.tiff", tiff_bytes)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        status_code=200,
        headers={
            "Content-Disposition": f"attachment; filename={payload.start_date}_{payload.end_date}_{payload.variable}.zip"
        }
    )

