import datetime

def months_interval(start_date, end_date):
  start = datetime.strptime(start_date, "%y-%m")
  end = datetime.strptime(end_date, "%y-%m")

  months_list = []
  actual = start

  while actual <= end:
    months_list.append(actual.strftime("%Y-%m"))

    if actual.month == 12:
      actual = datetime(actual.year + 1, 1, 1)
    else:
      actual = datetime(actual.year, actual.month + 1, 1)

    return months_list
