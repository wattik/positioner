from os import listdir
from os.path import isfile, join, splitext
from datetime import datetime as dt
from flask import Flask
from flask import request
from flask import send_file
import zipfile

app = Flask(__name__)


@app.route('/order-books', methods=["GET"])
def get_order_books():
    outputs_path = "./outputs"
    files = [f for f in listdir(outputs_path) if isfile(join(outputs_path, f))]

    start = request.args.get('start', None)
    end = request.args.get('end', None)

    filtered_files = get_files_by_range(start, end, files)

    # zip the files
    downloads_path = "./flask-api/downloads"
    archive_name = "outputs{}{}.zip".format("_start_{}".format(start) if start else "", "_end_{}".format(end) if end else "")

    zf = zipfile.ZipFile(join(downloads_path, archive_name), "w")
    for file in filtered_files:
        zf.write(join(outputs_path, file))
    zf.close()

    return send_file("./downloads/{}".format(archive_name), as_attachment=True)


def get_files_by_range(start: str, end: str, files: list):
    date_format = "%d-%m-%Y-%H-%M-%S"
    start_date = dt.strptime(start, date_format) if start else None
    end_date = dt.strptime(end, date_format) if end else None

    if start and end:
        print("Filtering files from '{}' to '{}'".format(start, end))
        return list(filter(lambda f: start_date < dt.strptime(splitext(f)[0], date_format) <= end_date, files))
    elif start:
        print("Filtering files from '{}'".format(start))
        return list(filter(lambda f: dt.strptime(splitext(f)[0], date_format) > start_date, files))
    elif end:
        print("Filtering files till {}".format(end))
        return list(filter(lambda f: dt.strptime(splitext(f)[0], date_format) <= end_date, files))
    else:
        print("Returning all files")
        return files


app.run()
