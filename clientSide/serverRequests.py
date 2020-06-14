# import torrentClient
import platform
import requests
import urllib
import queue
import json
import torf
import os

# TODO: make a proper wrapper

if platform.system() == "Windows":
    APP_FOLDER = os.path.join(os.getenv("LOCALAPPDATA"), "online_shop")
else:
    APP_FOLDER = os.path.expanduser(os.path.join("~", ".online_shop"))
os.makedirs(APP_FOLDER, exist_ok=True)

with open("config.json", "r") as f:
    CONFIG = json.load(f)

def get_torrent():
    temp_path = os.path.join(APP_FOLDER, "torrent")
    url = urllib.parse.urljoin(CONFIG["site"], "torrent")
    response = requests.get(url)
    with open(temp_path, "wb") as f:
        f.write(response.content)

    filename = get_torrent_name(temp_path) + ".torrent"
    os.rename(temp_path, os.path.join(os.path.split(temp_path)[0], filename))
    return filename

def get_server_pubkey():
    url = urllib.parse.urljoin(CONFIG["site"], "key")
    response = requests.get(url)
    with open(os.path.join(APP_FOLDER, "server.gpg"), "wb"):
        f.write(response.content)

def get_torrent_name(path):
    return torf.Torrent.read(path).metainfo["info"]["name"]

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
    torrentfile = get_torrent()
    print(torrentfile)
    # dl_torrent(torrentfile)
            