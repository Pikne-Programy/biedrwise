from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)