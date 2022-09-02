import zipfile
from xml.etree.ElementTree import iterparse


# readXlsx("mysheet.xlsx", sheet=1, header=True)
def read_xlsx(file_path, **args):

    if "sheet" in args:
        sheet = args["sheet"]
    else:
        sheet = 1
    if "header" in args:
        has_header = args["header"]
    else:
        has_header = False

    rows = []
    row = {}
    header = {}
    z = zipfile.ZipFile(file_path)

    # Get shared strings
    strings = [
        el.text
        for e, el in iterparse(z.open("xl/sharedStrings.xml"))
        if el.tag.endswith("}t")
    ]
    value = ""

    # Open specified worksheet
    for e, el in iterparse(z.open("xl/worksheets/sheet{}.xml".format(sheet))):
        # get value or index to shared strings
        if el.tag.endswith("}v"):  # <v>84</v>
            value = el.text
        if el.tag.endswith("}c"):  # <c r="A3" t="s"><v>84</v></c>

            # If value is a shared string, use value as an index
            if el.attrib.get("t") == "s":
                value = strings[int(value)]

            # split the row/col information so that the row leter(s) can be separate
            letter = el.attrib["r"]  # AZ22
            while letter[-1].isdigit():
                letter = letter[:-1]

            # if it is the first row, then create a header hash for the names
            # that COULD be used
            if not rows:
                header[letter] = value
            else:
                if value != "":

                    # if there is a header row, use the first row's names as the row hash index
                    if has_header and letter in header:
                        row[header[letter].lower()] = value
                    else:
                        row[letter] = value

            value = ""
        if el.tag.endswith("}row"):
            rows.append(row)
            row = {}
    z.close()

    rows.pop(0)

    return rows
