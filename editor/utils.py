import csv
import os
import re

from mysite import settings


def remove_comma(value: str) -> str:
    comma = ','
    value = re.sub(comma, '', value)
    return value


def get_abs_file_path(file_path: str) -> str:
    # file's url attribute contains file path with a forward slash
    # which creates wrong path with BASE_DIR so remove the forward slash
    abs_file_path = os.path.join(settings.BASE_DIR, file_path[1:])
    return abs_file_path


def read_csv_file(file_path: str, number_of_rows: int = None) -> list:
    header = None
    content = []
    dialect = None
    with open(file_path, newline='') as csv_file:
        sniffer = csv.Sniffer()
        has_header = False
        if sniffer.has_header(csv_file.read(2048)):
            has_header = True

        csv_file.seek(0)
        dialect = sniffer.sniff(csv_file.read(2048))

        csv_file.seek(0)
        csv_file_reader = csv.reader(csv_file, dialect=dialect)
        for row in csv_file_reader:
            if csv_file_reader.line_num == 1 and has_header:
                header = row
            else:
                content.append(row)

            if number_of_rows is not None and csv_file_reader.line_num == number_of_rows+1:
                break
    file_data = [header, content, dialect]
    return file_data


def update_csv_with_given_value(file_path: str, column_id: int, value: str):
    file_data = read_csv_file(file_path)
    header = file_data[0]
    content = file_data[1]
    dialect = file_data[2]
    with open(file_path, 'w', newline='') as csv_file:
        csv_file_writer = csv.writer(csv_file, dialect=dialect)
        if header:
            csv_file_writer.writerow(header)

        for row in content:
            if row[column_id] == value:
                csv_file_writer.writerow(row)


def update_csv_with_given_range(file_path: str, column_id: int, min: int, max: int):
    file_data = read_csv_file(file_path)
    header = file_data[0]
    content = file_data[1]
    dialect = file_data[2]

    for i in range(5):
        row = content[i]
        if not remove_comma(row[column_id]).isdigit():
            raise TypeError("values must be of numeric type for range updates")

    with open(file_path, 'w', newline='') as csv_file:
        csv_file_writer = csv.writer(csv_file, dialect=dialect)
        if header:
            csv_file_writer.writerow(header)

        for row in content:
            if (remove_comma(row[column_id]).isdigit() and
                    min <= int(remove_comma(row[column_id])) <= max):
                csv_file_writer.writerow(row)
