import serverRequests
import torrentClient
import platform
import wx
import wx.adv
import os

TRAY_TOOLTIP = 'Online Shop Torrent Client'
if platform.system() == "Linux":
    TRAY_ICON = os.path.join("GUIAssets", "icon", "icon_24.png")

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self,frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.myapp_frame = frame
        self.set_icon(TRAY_ICON)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Say Hello', self.on_hello)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print ('Tray icon was left-clicked.')

    def on_hello(self, event):
        print ('Hello, world!')

    def on_exit(self, event):
        self.myapp_frame.Close()

class My_Application(wx.Frame):

    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "", size=(1,1))
        panel = wx.Panel(self)
        self.myapp = TaskBarIcon(self)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    #----------------------------------------------------------------------
    def onClose(self, evt):
        """
        Destroy the taskbar icon and the frame
        """
        self.myapp.RemoveIcon()
        self.myapp.Destroy()
        self.Destroy()


if __name__ == "__main__":
    MyApp = wx.App()
    My_Application()
    MyApp.MainLoop()