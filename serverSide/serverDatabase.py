import mysql_to_sqlite3
import subprocess
import tempfile
import pymysql
import shutil
import random
import queue
import time
import json
import sys
import os

with open(os.path.join("..", "serverSide", "config.json"), "r") as f:
    CONFIG = json.load(f)

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
            itemdata = cursor.fetchone()
            cursor.execute("SELECT related_id FROM related_products WHERE prod_id = %s AND related_id IN (SELECT prod_id FROM products);", (id_, ))
            related = [i["related_id"] for i in cursor.fetchall()]
            cursor.execute("SELECT impath FROM images WHERE prod_id = %s;", (id_, ))
            images = [i["impath"] for i in cursor.fetchall()]
            return {
                "itemdata": itemdata,
                "related": related,
                "images": images
            }


    def add_release(self, name, path, torrent):
        with self.__connection.cursor() as cursor:
            cursor.execute("INSERT INTO releases VALUES (%s, %s, %s);", (name, path, torrent))
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
                mysql_tables = (
                    "products",
                    "related_products",
                    "images"
                )
            ).transfer()

            subprocess.run([Sz_APP_PATH, "a", os.path.join(out_path, "%s.7z" % timenow), outpath.name, "images/"])

        subprocess.run([GPG_APP_PATH, "--output", os.path.join(out_path, "%s.sig" % timenow), "--detach-sig", os.path.join(out_path, "%s.7z" % timenow)])

        file_storage = libtorrent.file_storage()
        libtorrent.add_files(file_storage, out_path)
        torrent_obj = libtorrent.create_torrent(file_storage)
        for trackerurl in CONFIG["trackers"]:
            torrent_obj.add_tracker(trackerurl)
        torrent_obj.set_comment("online_shop release id %d" % time.time())
        torrent_obj.set_creator("online_shop using libtorrent %s" % libtorrent.version)
        libtorrent.set_piece_hashes(torrent_obj, os.path.split(out_path)[0])
        torrent = torrent_obj.generate()
        with open(os.path.join(os.path.split(out_path)[0], os.path.split(out_path)[1] + ".torrent"), "wb") as f:
            f.write(libtorrent.bencode(torrent))

        


        # torrent = torf.Torrent(path = out_path, trackers=CONFIG["trackers"])
        # torrent.generate()
        # torrent.write(os.path.join(os.path.split(out_path)[0], os.path.split(out_path)[1] + ".torrent"))

        self.add_release(
            os.path.split(out_path)[-1],
            out_path,
            os.path.split(out_path)[-1] + ".torrent"
        )

        # return {
        #     "torrent": torrent,
        #     "torrentpath": os.path.join(os.path.split(out_path)[0], os.path.split(out_path)[1] + ".torrent")
        # }


if __name__ == "__main__":
    import libtorrent
    with ServerDatabase() as db:
        db.export_db()
