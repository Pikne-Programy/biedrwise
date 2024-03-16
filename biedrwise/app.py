# pylint: disable=missing-module-docstring
import os
import re
from sys import stderr
from pathlib import Path
from datetime import datetime, date
from flask import Flask, request, redirect, url_for, render_template

from db.db import DataBase
from ocr.reader import ocr_read

me = Path(__file__)
os.seteuid(os.stat(me).st_uid)
# os.setegid(os.stat(me).st_uid)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploaded"
db = DataBase("redis", 6379)

static_folder = Path("static")
upload_folder = static_folder / app.config["UPLOAD_FOLDER"]
upload_folder.mkdir(parents=True, exist_ok=True)

SUPPORTED_MIMETYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
}


def get_new_upload_filename():
    """
    Generate filename for new upload.
    Example: `2024-03-16T15_34_25.143617`
    """
    return datetime.today().isoformat().replace(":", "_")


@app.route("/receipt/<rec_id>", methods=["POST", "GET"])
def receipt(rec_id):
    if request.method == "POST":
        print("kurwa", repr(request.form), file=stderr)
        for k, v in request.form.items(multi=False):
            RE = r"^cb_(\d*)_(\d*)$"
            m = re.match(RE, k)
            a, b = m.group(1), m.group(2)
            print((a, b), file=stderr)
            # db.add_row_users(a, b)
        # lista indeks rowa -> lista id
        print(".", file=stderr)
        return redirect("/")
    else:
        data_list = [{**x,
                      'cb': [f'cb_{x.row_id}_{j}' for j in range(4)],
                      } for i, x in enumerate(db.print_receipt(rec_id))]
        data = db.get_receipt_data(rec_id)
        print(data_list, file=stderr)
        return render_template("home.html", dataList=data_list, head=data)


@app.route("/")
def spending():
    data_list = db.get_summary()
    print(data_list, file=stderr)
    usersList = [{"name": x[0], "debt": x[1]} for x in data_list]
    return render_template("user_debts.html", usersList=usersList)


@app.route("/receipts")
def receipts():
    # receipt_list = [
    #     {"date": "2024-03-10", "price": "12.00zł", 'src':'/receipt/0'},
    #     {"date": "2024-03-09", "price": "18.00zł", 'src':'/receipt/1'},
    #     {"date": "2024-02-28", "price": "123.00zł", 'src':'/receipt/2'},
    # ]
    receipt_list = db.get_receipts()
    print(receipt_list, file=stderr)
    receipt_list = [{**x, "src": f'/receipt/{int(x["payed"])}'} for x in receipt_list]
    return render_template("receipts.html", receipt_list=receipt_list)


@app.route("/add-receipt", methods=["GET", "POST"])
def add_receipt() -> str:
    """
    `/add-receipt` route
    GET: print upload file form
    POST: process uploaded file
    """
    if request.method == "POST":
        if "file" not in request.files or "who" not in request.form:
            return "ERROR: invalid request"
        file = request.files["file"]
        if not file:
            return "ERR: no file"
        if file.mimetype not in SUPPORTED_MIMETYPES:
            return f"ERR: {file.mimetype} is not supported"
        filename = f"{get_new_upload_filename()}.{SUPPORTED_MIMETYPES[file.mimetype]}"
        filepath = upload_folder / filename
        file.save(filepath)
        data = ocr_read(str(filepath.absolute()), file.mimetype == "application/pdf")
        print("\n" * 9, request.form, file=stderr)
        print("WHO", request.form["who"], file=stderr)
        rec_id = db.add_receipt(
            data, (date.today().isoformat(), 0.0, 0)
        )
        return redirect(url_for("receipt", rec_id=f"{rec_id}"))
    return render_template(
        "upload.html", ludzie="Marcin,Michał,Dominik,Gracjan".split(",")
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
