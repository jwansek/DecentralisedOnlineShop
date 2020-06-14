# import torrentClient
import subprocess
import platform
import requests
import tempfile
import urllib
import queue
import json
import torf
import os

# TODO: make a proper wrapper

with open("config.json", "r") as f:
    CONFIG = json.load(f)

if platform.system() == "Windows":
    APP_FOLDER = os.path.join(os.getenv("LOCALAPPDATA"), "online_shop")
    Sz = CONFIG["windows_7z_exec"]
    GPG = CONFIG["windows_gpg_exec"]
else:
    APP_FOLDER = os.path.expanduser(os.path.join("~", ".online_shop"))
    Sz = "7z"
    GPG = "gpg"

os.makedirs(APP_FOLDER, exist_ok=True)

def get_torrent():
    """Downloads the most recent release torrent

    Returns:
        str: the name correct name of the torrent file
    """
    temp_path = os.path.join(APP_FOLDER, "torrent")
    url = urllib.parse.urljoin(CONFIG["site"], "torrent")
    response = requests.get(url)
    with open(temp_path, "wb") as f:
        f.write(response.content)

    filename = get_torrent_name(temp_path) + ".torrent"
    os.rename(temp_path, os.path.join(os.path.split(temp_path)[0], filename))
    return filename

def get_server_pubkey():
    """Gets the server's public GPG key for validation and encrypting.
    It needs to get added to the clients keyring.
    """
    url = urllib.parse.urljoin(CONFIG["site"], "key")
    response = requests.get(url)
    with open(os.path.join(APP_FOLDER, "server.asc"), "wb") as f:
        f.write(response.content)

def get_torrent_name(path):
    """Returns the correct name of a torrent file

    Args:
        path (str): Path to a torrent file

    Returns:
        str: The correct name of the torrent file, as in the metadata
    """
    return torf.Torrent.read(path).metainfo["info"]["name"]

def encrypt_and_send(obj):
    """Encrypts a JSON-serialisable object and sends it so the server.
    The server's public key must be in the keyring otherwise this will
    error out. Probably should have used pickle instead so I can send
    custom class objects. Oh well.

    Args:
        obj (JSON-serialisable): A JSON-serialisable object to send
    """
    url = urllib.parse.urljoin(CONFIG["site"], "send")
    with tempfile.NamedTemporaryFile(suffix=".json") as plaintext_file:
        with open(plaintext_file.name, "w") as f:
            json.dump(obj, f)
        with tempfile.NamedTemporaryFile(suffix=".json.enc") as encrypted_file:
            subprocess.run([
                GPG, "--encrypt", "--yes", "-o", encrypted_file.name, 
                "-r", CONFIG["server_email"], plaintext_file.name
            ])
            
            with open(encrypted_file.name, "rb") as f:
                requests.post(url, files={"file": f})

def get_product(prod_id:int):
    """Gets all information about a given product. Requests the data from the server.
    Implemented to show that this is possible. In reality the user would use the local
    SQLite file so that the server is not required.

    Args:
        prod_id (int): A product id to search for

    Returns:
        dict: JSON reponse of the item
    """
    response = requests.get(CONFIG["site"]+"/api/product", params={"id":prod_id})
    return json.loads(response.content.decode())

#tempororary
def dl_torrent(torrentfile):
    class Main:
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

    main = Main()
    tc = torrentClient.TorrentClient(
        main.get_queue(), 
        os.path.join(APP_FOLDER, torrentfile), 
        APP_FOLDER,
    )
    tc.start()
    try:
        main.main()
    except KeyboardInterrupt:
        tc.stop_event.set() 

if __name__ == "__main__":
    # torrentfile = get_torrent()
    # print(torrentfile)
    # dl_torrent(torrentfile)

    # print(get_product(9197747))
            