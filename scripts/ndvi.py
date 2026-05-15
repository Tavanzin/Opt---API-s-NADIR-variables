import httpx
from auth import get_access_token

evalscript ="""
//VERSION=3
function setup() {
    return {
        input: ["B04", "B08", "dataMask"],
        output: [
          { id: "default", bands: 1, sampleType: "FLOAT32" },
          { id: "dataMask", bands: 1}
        ]  
    };
}

function evaluatePixel(samples) {
    let ndvi = index(samples.B08, samples.B04)

    return {
    default: [ndvi],
    dataMask: [samples.dataMask]
    }
}
"""

async def get_ndvi(coordinates):
  Token = await get_access_token()

  async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.post(
      url = "https://sh.dataspace.copernicus.eu/api/v1/statistics",

      headers = {
        "Authorization": f"Bearer {Token}",
        "Content-Type": "application/json"
      },

      json = {
        "input": {
          "bounds": {
            "geometry": {
              "type": "Polygon",
              "coordinates": [coordinates]
            },
            "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
          },
          "data": [{
            "type": "sentinel-2-l2a"
          }],
        },
        "aggregation": {
          "timeRange": {
            "from": "2025-01-01T00:00:00Z",
            "to": "2025-01-02T00:00:00Z"
          },
          "aggregationInterval": {"of": "P1D"},
          "evalscript": evalscript
        }
      }
    )

    return response.json()
