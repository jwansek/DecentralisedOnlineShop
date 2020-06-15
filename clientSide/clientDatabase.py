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
    
    proc = subprocess.Popen(
        [serverRequests.GPG, "--verify", os.path.join(path, name, name[6:]+".sig"), os.path.join(path, name, name[6:]+".sig")],
        stdout = subprocess.PIPE
    )
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        print(line.decode())

if __name__ == "__main__":
    import sys
    verify(sys.argv[1])

