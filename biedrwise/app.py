# pylint: disable=missing-module-docstring
import os
from sys import stderr
from pathlib import Path
from datetime import datetime
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

@app.route("/receipt/<rec_id>", methods=['POST', 'GET'])
def receipt(rec_id):
    if request.method == "POST":
        print(request.form, file=stderr)
        print('.', file=stderr)
        return redirect('/')
    else:
        data_list = [{**x, 'cb': [f'cb_{i}_{j}' for j in range(4)]} for i, x in enumerate(db.print_receipt(rec_id))]
        print(data_list, file=stderr)
        return render_template('home.html', dataList=data_list)

@app.route("/")
def spending():
    data_list = db.get_summary()
    usersList = [
        {"name": "Marcin Cpp", "debt": "10.00zł"},
        {"name": "Kret Kretes", "debt": "21.37zł"},
        {"name": "Michał Pobuta", "debt": "125.00zł"},
    ]
    return render_template("user_debts.html", usersList=usersList)

@app.route("/receipts")
def receipts():
    receipt_list = [
        {"date": "2024-03-10", "price": "12.00zł", 'src':'/receipt/0'},
        {"date": "2024-03-09", "price": "18.00zł", 'src':'/receipt/1'},
        {"date": "2024-02-28", "price": "123.00zł", 'src':'/receipt/2'},
    ]
    return render_template("receipts.html", receipt_list=receipt_list)

@app.route("/add-receipt", methods=["GET", "POST"])
def add_receipt() -> str:
    """
    `/add-receipt` route
    GET: print upload file form
    POST: process uploaded file
    """
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if not file:
            return "ERR: no file"
        if file.mimetype not in SUPPORTED_MIMETYPES:
            return f"ERR: {file.mimetype} is not supported"
        filename = f"{get_new_upload_filename()}.{SUPPORTED_MIMETYPES[file.mimetype]}"
        filepath = upload_folder / filename
        file.save(filepath)
        data = ocr_read(filepath, file.mimetype == "application/pdf")
        rec_id = db.add_receipt(data)
        return redirect(url_for("receipt", rec_id=f"{rec_id}"))
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
