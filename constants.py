data_file_name = "data.json"
wait_time = [10.0, 0.5]

def days(date: str) -> int:
    since_year = 1870
    months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    Date = date.split(".")
    day = int(Date[0])
    month = int(Date[1])
    year = int(Date[2])
    days = 0
    
    # check if date is 01.01.1 (date of birth missing)
    if day == 1 and month == 1 and year == 1:
        return -1
    
    days += day
    for m in range(month-1):
      days += months[m]
    if month > 2 and year % 4 == 0 and not year % 100 == 0:
      days += 1
    for y in range(since_year, year):
      days += 365
      if y % 4 == 0 and not y % 100 == 0:
        days += 1
    
    return days