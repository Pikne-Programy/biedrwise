from flask import Flask, render_template
from db.db import DataBase

app = Flask(__name__)
db = DataBase('redis', 6379)

@app.route("/")
def home():
    dataList = [
    {
        "name":"Cofe",
        "description":"Good beverage"
    },
    {
        "name":"Tea",
        "description":"Bad beverage"
    },
        {
        "name":"Blech",
        "description":"Awesome beverage (cures autism)"
    },
]
    return render_template("home.html", dataList = dataList)
@app.route("/recipe/<rec_id>")
def recipe(rec_id):
    data_list = db.print_recipe(rec_id)
    return render_template("home.html", dataList=data_list)

@app.route("/summary")
def spending():
    data_list = db.get_summary()
    return render_template("home.html", dataList=data_list)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)