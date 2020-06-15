import subprocess
import serverRequests
import sqlite3
import os

def add_to_keyring():
    serverRequests.get_server_pubkey()
    subprocess.run(
        [serverRequests.GPG, "--import", os.path.join(serverRequests.APP_FOLDER, "server.asc")]
    )

def verify(torrentfile):
    path = os.path.split(torrentfile)[0]
    name = os.path.split(torrentfile)[1].replace(".torrent", "")

    proc = subprocess.Popen([serverRequests.GPG, "--verify", os.path.join(path, name, name[6:]+".sig"), os.path.join(path, name, name[6:]+".7z")], stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        print(line)

def extract(torrentfile):
    path = os.path.split(torrentfile)[0]
    name = os.path.split(torrentfile)[1].replace(".torrent", "")

    subprocess.run([
        serverRequests.Sz,
        "x",
        os.path.join(path, name, name[6:]+".7z"),
        "-o"+os.path.join(path, "Database")
    ])

class ClientDatabase:
    def __enter__(self):
        self.__connection = sqlite3.connect(self.__find_db())
        return self

    def __exit__(self, type, value, traceback):
        self.__connection.close()

    def __find_db(self):
        base = os.path.join(serverRequests.APP_FOLDER, "Database")
        for file in os.listdir(base):
            if file[-3:] == ".db":
                return os.path.join(base, file)

    def get_products(self):
        cursor = self.__connection.cursor()
        cursor.execute("SELECT prod_id, title, category, weight, price, quantity FROM products;")
        out = cursor.fetchall()
        cursor.close()
        return out

if __name__ == "__main__":
    with ClientDatabase() as db:
        print(db.get_products())


