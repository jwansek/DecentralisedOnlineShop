import serverRequests
import subprocess
import threading
import urllib
import queue
import torf
import json
import sys
import os

class TorrentClient(threading.Thread):
    def __init__(self, q, torrentfile, loc):
        threading.Thread.__init__(self)
        self.q = q
        self.torrentfile = torrentfile
        self.loc = loc
        self.stop_event = threading.Event()

    def run(self):
        self.cwd = os.getcwd()
        os.chdir(self.loc)
        self.proc = subprocess.Popen(
            ["btdownloadheadless.py", self.torrentfile], 
            stdout=subprocess.PIPE
        )
        lastreportbuffer = TorrentClientReportBuffer()
        while not self.stop_event.isSet():
            line = self.proc.stdout.readline().decode().rstrip()
            if line == "":
                if not lastreportbuffer.is_empty():
                    self.lastreport = lastreportbuffer
                    self.q.put(self.lastreport)
                    lastreportbuffer.flush()
            else:
                lastreportbuffer.append(line)
        print("Seeding stopped...")
        os.chdir(self.cwd)
        self.proc.kill()

class TorrentClientReportBuffer:
    def __init__(self):
        self.flush()

    def __str__(self):
        out = ""
        out += "=================== REPORT BEGINS ===================\n"
        for i in self.buffer_contents:
            s = i.split(":")
            out += "%s:%s\n" % (s[0].replace(" ", "_"), s[1].strip())
        out += "=================== REPORT ENDS ==================="
        return out

    def is_empty(self):
        return self.buffer_contents == []

    def append(self, report):
        self.buffer_contents.append(report)
        s = report.split(":")
        setattr(self, s[0].replace(" ", "_"), s[1].strip())

    def flush(self):
        self.buffer_contents = []

def magnet_to_torrent(magnet, outpath):
    params = dict(
        urllib.parse.parse_qs(urllib.parse.urlsplit(magnet).query)
    )
    torrentobj = torf.Magnet(
        **{k: v[0] if len(v) == 1 else v for k, v in params.items()}
    ).torrent()
    torrentobj.metainfo["info"]["piece length"] = 16384
    print(torrentobj.write(outpath))

if __name__ == "__main__":
    #simple test program
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
    tc = TorrentClient(
        main.get_queue(), 
        "../local-exported/items-1591644340.torrent", 
        "../local-exported/"
    )
    tc.start()
    try:
        main.main()
    except KeyboardInterrupt:
        tc.stop_event.set()

