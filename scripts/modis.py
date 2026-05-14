import requests

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
    return response
