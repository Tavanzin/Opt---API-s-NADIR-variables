from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_bbox(n, s, w, e):
    return [w, n], [e, n], [e, s], [w, s], [w, n]

def get_coordinates(north, south, west, east):
  mid_lat = (north + south) / 2
  mid_lon = (west + east) / 2
  quadrantes = {
      "noroeste": get_bbox(north, mid_lat, west, mid_lon),
      "nordeste":  get_bbox(north, mid_lat, mid_lon, east),
      "sudoeste":  get_bbox(mid_lat, south, west, mid_lon),
      "sudeste":   get_bbox(mid_lat, south, mid_lon, east)
  }
  return quadrantes


## create an array with the months in the interval
def get_months_interval(start_date, end_date):
  start = datetime.strptime(start_date, "%Y-%m")
  end = datetime.strptime(end_date, "%Y-%m")

  months_list = []
  actual = start

  while actual <= end:
    months_list.append(actual.strftime("%Y-%m"))

    if actual.month == 12:
      actual = datetime(actual.year + 1, 1, 1)
    else:
      actual = datetime(actual.year, actual.month + 1, 1)

  return months_list

## Add a month to the date
def add_month(date) -> str:
  ## parse to datetime
  end_date_obj = datetime.strptime(date, "%Y-%m")
  ## add a month
  end_date_add = end_date_obj + relativedelta(months=1)
  ## parse to string
  end_date = end_date_add.strftime("%Y-%m")

  return end_date
