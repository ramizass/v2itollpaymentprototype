from flask import Flask, render_template
from db.mongo import get_transaksi

app = Flask(__name__)

@app.route("/")
def index():
    data = get_transaksi()
    return render_template("index.html", transaksi=data)

if __name__ == "__main__":
    app.run(debug=True, port=8000)