from pydantic import BaseModel, Field

class Copernicus(BaseModel):
    variable: str = Field(default="ndvi", description="Variavel da base de dados do Copernicus ['ndvi', 'fapar', 'lai' ou 'dem']")
    bbox: list[float] = Field(default=[42.3, 36.8, -9.7, -6.1], description="Coordenadas [north, south, west, east]")
    start_date: str = Field(default="2025-01", description="Data de início no formato YYYY-MM")
    end_date: str = Field(default="2025-02", description="Data de término no formato YYYY-MM")
