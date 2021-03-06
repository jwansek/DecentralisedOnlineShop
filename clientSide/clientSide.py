import serverRequests
import torrentClient
import clientDatabase
import platform
import random
import queue
import wx
import wx.adv
import os

TRAY_TOOLTIP = 'Online Shop Torrent Client'
if platform.system() == "Linux":
    TRAY_ICON = os.path.join("GUIAssets", "icon", "icon_24.png")
else:
    TRAY_ICON = os.path.join("GUIAssets", "icon", "icon_16.png")

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self,frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.myapp_frame = frame
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

        self.menu = None
        self.completed = os.path.exists(os.path.join(serverRequests.APP_FOLDER, "Database"))
        self.menu_items = {}
        self.queue = queue.Queue()

        clientDatabase.add_to_keyring()
        self.torrentfile = serverRequests.get_torrent()
        self.torrentclient = torrentClient.TorrentClient(
            self.queue,
            self.torrentfile,
            #"/home/edward/Downloads/debian-live-10.4.0-amd64-lxqt.iso.torrent",
            serverRequests.APP_FOLDER
        )
        self.torrentclient.start()
        wx.CallLater(200, self.afterFunc)

    def CreatePopupMenu(self):
        self.menu = wx.Menu()
        self.create_menu_item(self.menu, "Send example request", self.send_example_request, "example")
        self.create_menu_item(self.menu, "Get local database", self.print_database, "example2")
        self.menu.AppendSeparator()
        self.create_menu_item(self.menu, 'NameSpace', self.on_hello, "name")
        self.create_menu_item(self.menu, 'SizeSpace', self.doNothing, "space")
        self.create_menu_item(self.menu, 'StatusSpace', self.doNothing, "status")
        self.menu.AppendSeparator()
        self.create_menu_item(self.menu, 'Exit', self.on_exit, "exit")
        return self.menu

    def create_menu_item(self, menu, label, func, internalkey):
        self.menu_items[internalkey] = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=self.menu_items[internalkey].GetId())
        menu.Append(self.menu_items[internalkey])
        return self.menu_items[internalkey]

    def doNothing(self):
        pass
    
    def afterFunc(self):
        if self.menu is not None:
            # a horrible hack but it works
            try:
                self.menu.IsAttached()
            except RuntimeError:
                self.menu = None
                self.menu_items = {}

        if self.menu_items != {}:
            self.update_menu()
        
        wx.CallLater(200, self.afterFunc)

    def update_menu(self):
        report = None
        try:
            while True:
                report = self.queue.get_nowait()
        except queue.Empty:
            pass

        if report is not None:
            # print(report)
            self.menu_items["name"].SetItemLabel(report.name)
            self.menu_items["space"].SetItemLabel("%s - %s" % (report.tot_size, report.progress))
            self.menu_items["status"].SetItemLabel("%s↑ %s↓" % (report.upload_rate, report.download_rate))

            if report.state == "seeding" and not os.path.exists(os.path.join(serverRequests.APP_FOLDER, "Database")):
                self.on_torrent_completed()

    def print_database(self, _):
        if self.completed:
            with clientDatabase.ClientDatabase() as db:
                print(db.get_products())
        else:
            print("The torrent has not yet completed")

    def on_torrent_completed(self):
        print("Torrent completed")
        clientDatabase.extract(self.torrentfile)
        self.completed = True

    def send_example_request(self, _):
        serverRequests.encrypt_and_send({
            "user_id": random.randint(0, 10000000),
            "order": [
                {9197747: 1},
                {1000001431104: 3},
                {1000001430564: 14},
                {1000002091711: random.randint(1, 9)},
                {1000001431043: random.randint(1, 9)}
            ]
        })

    def set_icon(self, path):
        icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print ('Tray icon was left-clicked.')

    def on_hello(self, event):
        print ('Hello, world!')

    def on_exit(self, event):
        self.myapp_frame.Close()

class Application(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(1,1))
        panel = wx.Panel(self)
        self.myapp = TaskBarIcon(self)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, evt):
        """
        Destroy the taskbar icon and the frame
        """
        self.myapp.torrentclient.stop_event.set()
        del self.myapp.torrentclient
        self.myapp.RemoveIcon()
        self.myapp.Destroy()
        self.Destroy()


if __name__ == "__main__":
    app = wx.App()
    Application()
    app.MainLoop()
