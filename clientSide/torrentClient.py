import libtorrent
import threading
import urllib
import queue
import json
import time
import sys
import os

def size_to_str(size:int):
    KB = 1024.0
    MB = KB * KB
    GB = MB * KB
    if size >= GB:
        return ('{:,.2f} GB').format(size / GB)
    elif size >= MB:
        return ('{:,.1f} MB').format(size / MB)
    elif size >= KB:
        return ('{:,.1f} kB').format(size / KB)
    else:
        return ('{} bytes').format(size)

def get_torrent_name(path):
    torrent_file = libtorrent.bdecode(open(path, "rb").read())
    return libtorrent.torrent_info(torrent_file).name()

class TorrentClient(threading.Thread):
    def __init__(self, q, torrentfile, loc, after=500, seeding_mode=False):
        threading.Thread.__init__(self)
        self.q = q
        self.torrentfile = torrentfile
        self.loc = loc
        self.after = after
        self.stop_event = threading.Event()
        self.seeding_mode = seeding_mode

    def run(self):
        session = libtorrent.session()
        session.listen_on(6881, 6891)
        if self.seeding_mode:
            dl_obj = session.add_torrent({
                "ti": libtorrent.torrent_info(self.torrentfile),
                "save_path": self.loc,
                "seed_mode": True
            })
        else:
            dl_obj = session.add_torrent({
                "ti": libtorrent.torrent_info(self.torrentfile),
                "save_path": self.loc
            })
        tot_size = str(dl_obj.status().total_wanted)
        name = dl_obj.name()
        reportBuffer = TorrentClientReportBuffer(tot_size, name)
        while not self.stop_event.isSet():
            reportBuffer.change_status(dl_obj.status())
            self.q.put(reportBuffer)
            time.sleep(self.after/1000)
        del session
        print("Downloading/Seeding Halted...")

class TorrentClientReportBuffer:
    STATE_STR = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
    def __init__(self, tot_size, name):
        self.tot_size = size_to_str(int(tot_size))
        self.name = name

    def change_status(self, status):
        self.progress = "%.2f%%" % (status.progress * 100)
        self.download_rate = "%s/s" % (size_to_str(status.download_rate))
        self.upload_rate = "%s/s" % (size_to_str(status.upload_rate))
        self.num_peers = status.num_peers
        self.state = self.STATE_STR[status.state]

    def __str__(self):
        return "%s - %s\n%s complete | %s down | %s up | %i peers | %s" % (
            self.name,
            self.tot_size,
            self.progress,
            self.download_rate,
            self.upload_rate,
            self.num_peers,
            self.state
        )
