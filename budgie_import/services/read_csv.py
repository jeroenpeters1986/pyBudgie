import csv


def read_csv(file_path, **args):
    # if "header" in args:
    #     has_header = args["header"]
    # else:
    #     has_header = False

    rows = []

    # opening the CSV file
    with open(file_path, mode="r") as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            rows.append({key.lower(): value for key, value in zip(headers, row)})

    return rows
