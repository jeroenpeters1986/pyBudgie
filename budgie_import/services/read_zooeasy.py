import xml.etree.ElementTree as ET

def read_zooeasy(file_path):
    rows = []

    tree = ET.parse(file_path)
    root = tree.getroot()

    for dier in root.findall('Dier'):
        item = {}
        for child in dier:
            item[child.tag.lower()] = child.text
        rows.append(item)

    print(rows)
    return []

    return rows
