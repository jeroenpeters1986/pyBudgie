import csv


def read_csv(file_path, **args):

    # if "header" in args:
    #     has_header = args["header"]
    # else:
    #     has_header = False

    # opening the CSV file
    with open(file_path, mode="r") as file:

        # reading the CSV file
        csvFile = csv.reader(file)

        # displaying the contents of the CSV file
        for lines in csvFile:
            print(lines)

        return csvFile
