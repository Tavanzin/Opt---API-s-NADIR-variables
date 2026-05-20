import requests

from auth.CopernicusAuth import get_Copernicus_accessToken 

evalscript = """
///VERSION=3
function setup() {
  return {
    input: ["DEM"],
    output: [ { bands: 1 } ]
  }
}

function evaluatePixel(sample) {
  return [sample.DEM / 2000]
}
"""

async def post_dem():
    Token = await get_Copernicus_accessToken()
    
    url = "https://sh.dataspace.copernicus.eu/api/v1/process"
    header = {
        "Authorization": f"Bearer {Token}",
        "Content-Type": "application/json"
    }
    Payload = {
        "input": {
            "bounds": {
                "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
                "bbox": [-9.7, 36.8, -6.1, 42.3]
            },
            "data": [{
                "type": "dem",
                "dataFilter": {"demInstance": "COPERNICUS_30"}
            }],
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [{
                "identifier": "default",
                "format": {"type": "image/tiff"}
            }]
        },
        "evalscript": evalscript
    }
    response = requests.post(url=url, headers=header, json=Payload)
    if response.status_code != 200:
        return {"erro": response.status_code, "detalhes": response.text}
    return response.content
