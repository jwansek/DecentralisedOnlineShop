import serverDatabase
import threading
import shutil
import flask
import time
import os
app = flask.Flask(__name__)

@app.route("/torrent")
def get_torrent():
    with serverDatabase.ServerDatabase() as db:
        filename = db.get_newest_release()["torrent"]
    return app.send_static_file(filename)

# e.g. `http://localhost:5000/api/product?id=9197747`
@app.route("/api/product")
def get_product():
    prod_id = flask.request.args.get("id", type=int)
    with serverDatabase.ServerDatabase() as db:
        return flask.jsonify(db.get_product(prod_id))

@app.route("/")
def hello_world():
    return "Hello World!"

def copy_torrent_file():
    with serverDatabase.ServerDatabase() as db:
        newest_release = db.get_newest_release()

    shutil.copy2(os.path.join(os.path.split(newest_release["path"])[0], newest_release["torrent"]), "static")

if __name__ == "__main__":
    copy_torrent_file()
    
    # app.run()
    app.run(host='0.0.0.0',debug=False)