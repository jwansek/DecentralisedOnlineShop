import libtorrent
import queue
import sys
import os
sys.path.append(os.path.join("..", "clientSide"))
import torrentClient
import serverDatabase

class ServerTorrentClient:
    def __init__(self):
        self.queue = queue.Queue()

    def get_queue(self):
        return self.queue

    def main(self, verbose=False):
        while True:
            report = None
            try:
                while True:
                    report = self.queue.get_nowait()
            except queue.Empty:
                pass

            if report is not None and verbose:
                print(report)

def seed(release=False):
    with serverDatabase.ServerDatabase() as db:
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
        stc.main(verbose=True)
    except KeyboardInterrupt:
        tc.stop_event.set()
        del stc
        print("\nExiting nicely...\n")

if __name__ == "__main__":
    seed()

