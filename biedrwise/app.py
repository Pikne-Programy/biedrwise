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

@app.route("/user_debts")
def users():
    usersList = [
        {
            "name":"Marcin Cpp",
            "debt":"10.00zł"
        },
        {
            "name":"Kret Kretes",
            "debt":"21.37zł"
        },
        {
            "name":"Michał Pobuta",
            "debt":"125.00zł"
        }
    ]
    return render_template("user_debts.html", usersList=usersList)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)