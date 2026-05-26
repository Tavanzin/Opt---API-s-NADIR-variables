from pydantic import BaseModel, Field

class modisRequest(BaseModel):
    band: str = Field(default="ET", description="The band to retrieve (e.g., 'ET' or 'LE').")
    lat: float = Field(default=39.7, description="Latitude of the location.")
    lon: float = Field(default=-8.1, description="Longitude of the location.")
    start_date: str = Field(default='2025001', description="Start date in the format 'YYYYDDD' (e.g., '2025001').")
    end_date: str = Field(default='2025087', description="End date in the format 'YYYYDDD' (e.g., '2025087').")
