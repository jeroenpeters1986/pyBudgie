from django.utils.dateparse import parse_date


def make_date(date):
    try:
        return parse_date(date)
    except TypeError:
        return date
