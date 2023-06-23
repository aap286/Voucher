from datetime import date, datetime

# today's date
today = datetime.strptime("2023/6/2", "%Y/%m/%d")


def print_year_range(date):
    month = date.month
    year = date.year

    if month < 4:
        year -= 1

    return "/{}-{}".format(year, str(year + 1)[-2:])


ans = print_year_range(today)
print(ans)
