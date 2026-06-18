from auth.CopernicusAuth import get_Copernicus_accessToken
from controllers.CopernicusController import add_month

import httpx

evalscript = """
//VERSION=3
function setup() {
    return {
        input: ["B04", "B08", "dataMask", "SCL"],
        output: { bands: 1, sampleType: "FLOAT32" }
    };
}
function evaluatePixel(sample) {
    if (sample.dataMask !== 1 || [3, 8, 9, 10, 11].includes(sample.SCL)) {
        return [NaN];
    }
    let val = index(sample.B08, sample.B04);
    return [val];
}
"""

async def post_ndvi(coordinates, start_date, end_date):
  ## add a month to ensure the request of the month
  end_date = add_month(end_date)

  Token = await get_Copernicus_accessToken()
  
  async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.post(
      url = "https://sh.dataspace.copernicus.eu/api/v1/process",

      headers = {
        "Authorization": f"Bearer {Token}",
        "Content-Type": "application/json",
        "Accept": "image/tiff"
      },

      json = {
        "input": {
          "bounds": {
            "geometry": {
              "type": "Polygon",
              "coordinates": [coordinates]
            },
            "properties": { "crs": "http://www.opengis.net/def/crs/EPSG/0/4326" },
          },
          "data": [{
            "type": "sentinel-2-l2a",
            "dataFilter": {
              "timeRange": {
                "from": f"{start_date}-01T00:00:00Z",
                "to": f"{end_date}-01T00:00:00Z"
              },
              "maxCloudCoverage": 30,
              "mosaickingOrder": "leastCC",
            }
          }]
        },
        "output": {
          "width": 512,
          "height": 512,
          "responses": [
            {
                "identifier": "default",
                "format": {
                    "type": "image/tiff"
                }
            }
        ]
      },
        "evalscript": evalscript
      }
    )
    
  return response.content
