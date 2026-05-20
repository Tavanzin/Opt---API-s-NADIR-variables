from fastapi import APIRouter
from fastapi.responses import Response, StreamingResponse
import io
import zipfile

from controllers.CopernicusController import get_months_interval, get_coordinates

from scripts.ndvi import post_ndvi
from scripts.fapar import post_fapar
from scripts.lai import post_lai
from scripts.dem import post_dem

import asyncio

router = APIRouter()

@router.get("/ndvi")
async def GetParams(north: float = 42.3, south: float = 36.8,
                    west: float = -9.7, east: float = -6.1,
                    start_date :str = '2025-01', end_date :str = '2025-01'
                    ):
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

@router.get("/fapar")
async def GetParams(north: float = 42.3, south: float = 36.8,
                    west: float = -9.7, east: float = -6.1,
                    start_date :str = '2025-01', end_date :str = '2025-01'
                    ):
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

@router.get("/lai")
async def GetParams(north: float = 42.3, south: float = 36.8,
                    west: float = -9.7, east: float = -6.1,
                    start_date :str = '2025-01', end_date :str = '2025-01'
                    ):
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
async def callAPI():
   demTiff = await post_dem()
   return Response(content=demTiff, media_type="image/tiff")
