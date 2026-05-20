from fastapi import FastAPI, APIRouter
from routes import Copernicus, Modis

app = FastAPI()
router = APIRouter()

app.include_router(Copernicus.router, prefix='/Copernicus', tags=["Copernicus"])
app.include_router(Modis.router, prefix='/Modis', tags=["Modis"])
