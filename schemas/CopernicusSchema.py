from pydantic import BaseModel, Field

class Copernicus(BaseModel):
    variable: str = Field(default="ndvi", description="Variavel da base de dados do Copernicus")
    bbox: list[float] = Field(default=[42.3, 36.8, -9.7, -6.1], min_items=4, max_items=4, description="Lista de 4 floats representando a caixa delimitadora (min_lon, min_lat, max_lon, max_lat)")
    start_date: str = Field(default="2025-01", description="Data de início no formato YYYY-MM")
    end_date: str = Field(default="2025-02", description="Data de término no formato YYYY-MM")
