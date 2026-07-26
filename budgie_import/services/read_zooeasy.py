import xml.etree.ElementTree as ET


def _clean_text(value):
    if value is None:
        return ""
    return value.strip()


def _map_gender(raw_value):
    value = _clean_text(raw_value)
    if value in {"1", "female", "vrouw", "pop"}:
        return "1"
    if value in {"0", "male", "man"}:
        return "0"
    return value


def read_zooeasy(file_path):
    rows = []

    tree = ET.parse(file_path)
    root = tree.getroot()

    for dier in root.findall("Dier"):
        item = {}
        for child in dier:
            tag = child.tag.lower()
            value = _clean_text(child.text)

            if tag == "registratienummer":
                item["ringnummer"] = value
            elif tag == "geboortedatum":
                item["geboren"] = value
            elif tag == "overlijdingsdatum":
                item["overleden"] = value
            elif tag == "geslacht":
                item["geslacht"] = _map_gender(value)
            elif tag == "registratienummervader":
                item["vader"] = value
            elif tag == "registratienummermoeder":
                item["moeder"] = value
            elif tag == "kleur":
                item["kleur"] = value
            else:
                item[tag] = value

        rows.append(item)

    return rows
