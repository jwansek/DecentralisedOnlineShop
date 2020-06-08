import mysql_to_sqlite3
import subprocess
import tempfile
import pymysql
import shutil
import random
import queue
import torf
import time
import json
import sys
import os

with open(os.path.join("..", "serverSide", "config.json"), "r") as f:
    CONFIG = json.load(f)

sys.path.append(os.path.join("..", "clientSide"))
import torrentClient


Sz_APP_PATH = "7z"
GPG_APP_PATH = "gpg"

class ServerDatabase:
    def __enter__(self):
        self.__connection = pymysql.connect(
            host = CONFIG["host"],
            port = CONFIG["port"],
            user = CONFIG["user"],
            passwd = CONFIG["passwd"],
            db = CONFIG["database"],
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor
        )
        return self

    def __exit__(self, type, value, traceback):
        self.__connection.close()

    def add_product(self, page_rip):
        if self.id_in_db(page_rip["id"]):
            print("Skipping id...")
            return


        with self.__connection.cursor() as cursor:
            cursor.execute("INSERT INTO products VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (
                page_rip["id"],
                page_rip["title"],
                page_rip["category"],
                page_rip["weight"],
                page_rip["price"],
                random.randint(0, 12),
                page_rip["prod_info"],
                page_rip["nutritional_info"],
                page_rip["storage_info"]
            ))
            #TODO: get executemany() working here (wont be a noticable preformance improvement)
            for related_id in page_rip["related"]:
                cursor.execute("INSERT INTO related_products VALUES (%s, %s);", (page_rip["id"], related_id))
            for impath in page_rip["impaths"]:
                cursor.execute("INSERT INTO images VALUES (%s, %s);", (page_rip["id"], impath))
        self.__connection.commit()

    def update_image(self, id_, impaths):
        print(id_, impaths)

    def id_in_db(self, id_):
        return bool(self.get_product(id_ ))

    def get_product(self, id_):
        with self.__connection.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE prod_id = %s", (id_, ))
            return cursor.fetchall()

    def add_release(self, name, path, magnet, torrent):
        with self.__connection.cursor() as cursor:
            cursor.execute("INSERT INTO releases VALUES (%s, %s, %s, %s);", (name, path, magnet, torrent))
        self.__connection.commit()

    def get_newest_release(self):
        with self.__connection.cursor() as cursor:
            cursor.execute("SELECT * FROM releases ORDER BY SUBSTRING(name, 7) DESC LIMIT 1;")
            return cursor.fetchone()
    

    def export_db(self):
        out_path = os.path.join("..", "local-exported", "items-%d" % time.time())
        cwd = os.getcwd()
        if os.path.exists(os.path.split(out_path)[0]):
            shutil.rmtree(os.path.split(out_path)[0])
        os.makedirs(out_path)

        timenow = str(int(time.time()))
        with tempfile.NamedTemporaryFile(prefix = timenow, suffix = ".db") as outpath:
            mysql_to_sqlite3.MySQLtoSQLite(
                mysql_database = CONFIG["database"],
                mysql_user = CONFIG["user"],
                mysql_password = CONFIG["passwd"],
                mysql_host = CONFIG["host"],
                mysql_port = CONFIG["port"],
                sqlite_file = outpath.name,
                tables = [
                    "products",
                    "related_products",
                    "images"
                ]
            ).transfer()

            subprocess.run([Sz_APP_PATH, "a", os.path.join(out_path, "%s.7z" % timenow), outpath.name, "images/"])

        subprocess.run([GPG_APP_PATH, "--output", os.path.join(out_path, "%s.sig" % timenow), "--detach-sig", os.path.join(out_path, "%s.7z" % timenow)])

        torrent = torf.Torrent(path = out_path, trackers=CONFIG["trackers"])
        torrent.generate()
        torrent.write(os.path.join(os.path.split(out_path)[0], os.path.split(out_path)[1] + ".torrent"))
        magnet =  str(torrent.magnet())

        self.add_release(torrent.name, str(torrent.path), magnet, torrent.name + ".torrent")

        return {
            "torrent": torrent,
            "torrentpath": os.path.join(os.path.split(out_path)[0], os.path.split(out_path)[1] + ".torrent"),
            "magnet": magnet
        }

class ServerTorrentClient:
    def __init__(self):
        self.queue = queue.Queue()

    def get_queue(self):
        return self.queue

    def main(self):
        while True:
            report = None
            try:
                while True:
                    report = self.queue.get_nowait()
            except queue.Empty:
                pass

            if report is not None:
                print(report)

def seed(release=False):
    with ServerDatabase() as db:
        if release:
            db.export_db()
        torrentinfo = db.get_newest_release()

    stc = ServerTorrentClient()
    tc = torrentClient.TorrentClient(
        stc.get_queue(),
        os.path.join(os.path.split(torrentinfo["path"])[0], torrentinfo["torrent"]),
        os.path.split(torrentinfo["path"])[0]
    )
    tc.start()
    try:
        stc.main()
    except KeyboardInterrupt:
        tc.stop_event.set()
        del stc
        print("\nExiting nicely...\n")
    



if __name__ == "__main__":
    seed()
