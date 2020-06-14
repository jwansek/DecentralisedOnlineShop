import serverRequests
import libtorrent
import threading
import urllib
import queue
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

