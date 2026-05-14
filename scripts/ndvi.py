import requests
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

def get_ndvi(coordinates):
  Token = get_access_token()
  url = "https://sh.dataspace.copernicus.eu/api/v1/statistics"

  header = {
    "Authorization": f"Bearer {Token}",
    "Content-Type": "application/json"
  }

  Payload = {
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
      "to": "2025-04-01T00:00:00Z"
    },
    "aggregationInterval": {"of": "P1D"},
    "evalscript": evalscript
  }
}

  response = requests.post(url=url, headers=header, json=Payload)
  return response.json()
