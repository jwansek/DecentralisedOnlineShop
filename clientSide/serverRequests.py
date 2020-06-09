import requests
import urllib
import json

# TODO: make a proper wrapper

with open("config.json", "r") as f:
    CONFIG = json.load(f)

def get_torrent():
    url = urllib.parse.urljoin(CONFIG["site"], "torrent")
    response = requests.get(url)
    return json.loads(response.text)
            