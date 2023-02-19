import threading
import time
import wx
from wx.py.shell import ShellFrame as Frame
import numpy as np


class GUI(threading.Thread):


    def __init__(self):
        threading.Thread.__init__(self)
        self.clickQueue = []


    def run(self):
        self.app = wx.App()
        self.frame = Frame(None, title=str(threading.current_thread()))
        # wx._core._wxPyCleanup()

        self.frame = wx.Frame(None, -1, 'win.py')
        self.frame.SetSize(0, 0, 200, 50)
        self.panel = wx.Panel(self.frame, wx.ID_ANY)

        self.create_components()

        self.frame.Show()
        self.frame.Centre()

        self.counter = 1
        self.app.MainLoop()
        # self.app_thread = threading.Thread(target=self.app.MainLoop)
        # self.app_thread.start()

    def create_components(self):
        self.create_button(wx.ID_ANY, 'Test', (10, 10), self.default_callback)

    def create_button(self, id, text, position, callback_function):
        button = wx.Button(self.panel, id, text, position)
        button.Bind(wx.EVT_BUTTON, self.default_thread_callback)

    def default_thread_callback(self, event):
        callback_thread = threading.Thread(target=self.default_callback, args=[event])
        callback_thread.start()

    def default_callback(self, event):
        self.clickQueue.append(self.counter)
        self.counter += 1
