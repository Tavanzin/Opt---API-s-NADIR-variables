import requests
import json

def get_modis(band, lat, lon, start_date, end_date):
    band = band.strip()
    start_date = start_date.strip()
    end_date = end_date.strip()

    # "https://modis.ornl.gov/rst/api/v1/MOD16A2/subset?latitude={lat}&longitude={lon}&startDate=A{start_date}&endDate=A{end_date}&product=MOD16A2&band={band}&kmAboveBelow=0&kmLeftRight=0"
    url = (
        f"https://modis.ornl.gov/rst/api/v1/MOD16A2/subset?"
        f"latitude={lat}&longitude={lon}"
        f"&startDate=A{start_date}&endDate=A{end_date}"
        f"&product=MOD16A2&band={band}"
        f"&kmAboveBelow=0&kmLeftRight=0"
    )

    print(f"url criado: {url}")

    response = requests.get(url)

    subset = response.json().get("subset", [])
    result = []

    for item in subset:
      values = item.get("data", [])
      validValue = [v for v in values if v > -9000 & v < 32700]
      if validValue:
         mean = sum(validValue) / len(validValue)
      
      else:
         mean = 0
      result.append({
         "calendar_date": item["calendar_date"],
        "average_value": round(mean, 2),
        "pixel_count": len(validValue)
      })
    with open(f"outputs/{start_date}_{end_date}-{band}-{lat}_{lon}.json", "w", encoding="utf-8") as f:
       json.dump(result, f, indent=4, ensure_ascii=False)

    return result
