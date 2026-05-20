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
