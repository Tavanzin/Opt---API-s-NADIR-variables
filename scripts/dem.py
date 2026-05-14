import requests
from auth import get_access_token

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

def get_dem():
    Token = get_access_token()
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
            "response": [{
                "identifier": "default",
                "format": {"type": "image/tiff"}
            }]
        },
        "evalscript": evalscript
    }
    response = requests.post(url=url, headers=header, json=Payload)
    if response.status_code != 200:
        return {"erro": response.status_code, "detalhes": response.text}
    return {"status": "sucesso", "codigo": response.status_code, "Response": response}
