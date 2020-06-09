import serverDatabase
import threading
import flask
import time
import os
app = flask.Flask(__name__)

@app.route("/torrent")
def get_torrent():
    with serverDatabase.ServerDatabase() as db:
        return flask.jsonify(db.get_newest_release())

# e.g. `http://localhost:5000/api/product?id=9197747`
@app.route("/api/product")
def get_product():
    prod_id = flask.request.args.get("id", type=int)
    with serverDatabase.ServerDatabase() as db:
        return flask.jsonify(db.get_product(prod_id))

@app.route("/")
def hello_world():
    return "Hello World!"

if __name__ == "__main__":
    # app.run()
    app.run(host='0.0.0.0',debug=False)