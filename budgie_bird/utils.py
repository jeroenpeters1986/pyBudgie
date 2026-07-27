import re

from django.utils.dateparse import parse_date


def make_date(date):
    try:
        return parse_date(date)
    except TypeError:
        return date


def format_ringnumber(text):
    text = str(text or "").strip().upper()
    if not text:
        return None

    ringnumber_regex = re.compile(
        r"(?P<breeder>[A-Z0-9]{3,4})\s*-\s*(?P<serial_num>[0-9]{2,3})\s*-\s*(?P<year>\d{4})",
        re.IGNORECASE,
    )

    text = text.replace(" ", "")
    match = ringnumber_regex.search(text)
    if not match:
        return text

    breeder = match.group("breeder").upper()
    serial_num = match.group("serial_num").zfill(3)
    year = match.group("year")

    return f"{breeder}-{serial_num}-{year}"
