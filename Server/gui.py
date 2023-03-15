import threading
import time
import wx
from wx.py.shell import ShellFrame as Frame
import numpy as np
from typing import List, Tuple, Union
import math_funcs


class GUI(threading.Thread):

    OBJECT_RADIUS = 5
    CONE_BRUSH = None
    FIELD_START_X = 50
    FIELD_END_X = 550
    FIELD_START_Y = 50
    FIELD_END_Y = 350
    FIELD_START_X_METERS = -3
    FIELD_END_X_METERS = 3
    FIELD_START_Y_METERS = -3
    FIELD_END_Y_METERS = 3
    panel = None
    frame = None
    paint_dc = None
    memory_dc = None
    paint_lock = None
    app = None
    counter = 0
    bitmap = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.clickQueue = []

    def run(self):
        self.app = wx.App()
        self.CONE_BRUSH = wx.Brush('yellow')

        self.paint_lock = threading.Lock()
        self.frame = Frame(None, title=str(threading.current_thread()))
        # wx._core._wxPyCleanup()

        self.frame = wx.Frame(None, -1, 'win.py')
        self.frame.SetSize(0, 0, 1000, 1000)
        self.panel = wx.Panel(self.frame, wx.ID_ANY)
        self.paint_dc = wx.ClientDC(self.panel)
        self.bitmap = wx.Bitmap(500, 500)

        self.frame.Show()
        self.frame.Centre()

        self.create_components()
        self.counter = 1
        self.app.MainLoop()

    def create_components(self):
        self.create_field()

    def create_button(self, id, text, position, callback_function):
        button = wx.Button(self.panel, id, text, position)
        button.Bind(wx.EVT_BUTTON, self.default_thread_callback)

    def create_field(self):
        if self.paint_dc:
            self.paint_lock.acquire()
            self.paint_dc.SetPen(wx.Pen('black', 10))
            self.paint_dc.SetBrush(wx.Brush('gray'))
            self.paint_dc.DrawRectangle(self.FIELD_START_X, self.FIELD_START_Y, self.FIELD_END_X - self.FIELD_START_X,
                                        self.FIELD_END_Y - self.FIELD_START_Y)
        self.paint_lock.release()

    def _scale_to_field(self, x: float, y: float) -> Tuple[int, int]:

        x = int(math_funcs.dead_band(x, (self.FIELD_START_X_METERS, self.FIELD_START_X), (self.FIELD_END_X_METERS, self.FIELD_END_X)))
        y = int(math_funcs.dead_band(y, (self.FIELD_START_Y_METERS, self.FIELD_START_Y), (self.FIELD_END_Y_METERS, self.FIELD_END_Y)))

        return x, y

    def draw_cones(self, cones: List[Tuple[float, float]]):
        """
        draws a cone (yellow circle) on the screen
        :param x_list: all object x positions
        :param y_list: all object y positions
        :return:
        """

        if self.panel and self.paint_dc:

            self.create_field()

            for cone in cones:
                x, y = self._scale_to_field(*cone[:2])
                print("draw", x, y)

                self.paint_dc.SetPen(wx.Pen('black', 1))
                self.paint_dc.SetBrush(self.CONE_BRUSH)
                self.paint_dc.DrawCircle(x, y, self.OBJECT_RADIUS)

    def default_thread_callback(self, event):
        callback_thread = threading.Thread(target=self.default_callback, args=[event])
        callback_thread.start()

    def default_callback(self, event):
        self.clickQueue.append(self.counter)
        self.counter += 1
