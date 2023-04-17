import wx
import time
import threading
from pubsub import pub
from win32api import GetSystemMetrics
from typing import List, Tuple
import math_funcs

app = wx.App(False)

BACKGROUND_COLOR = wx.LIGHT_GREY
SCREEN_HEIGT = GetSystemMetrics(1)
SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGT)
DIRECTION_BUTTON_SIZE = (int(SCREEN_WIDTH / 16), int(SCREEN_HEIGT / 16))
CLICK_LENGTH_MS = 500

#background pictures
LOGIN_SCREEN_BACKGROUND = wx.Image(r"gui_pictures\login_screen_background.png", wx.BITMAP_TYPE_ANY).Rescale(SCREEN_WIDTH, SCREEN_HEIGT).ConvertToBitmap()

class MainPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.frame = parent
        self.SetBackgroundColour(BACKGROUND_COLOR)
        box = wx.BoxSizer()

        self.user = ""

        # creating all panels
        self.login = LoginPanel(self, self.frame)
        # self.registration = RegistrationPanel(self, self.frame)
        self.control = ControlPanel(self, self.frame)

        box.Add(self.login)
        # box.Add(self.registration)
        box.Add(self.control)


        # showing the opening panel
        self.login.Show()
        self.SetSizer(box)
        self.Layout()


class MainFrame(wx.Frame):

    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent, title="robotics camera network", size=SCREEN_SIZE)
        wx.Frame.__init__(self, None, title="Main App")

        # create main panel
        main_panel = MainPanel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(main_panel, 1, wx.EXPAND)

        self.CreateStatusBar(1)
        self.SetStatusText("robotics camera network")

        # show the frame
        self.SetSizer(box)
        self.Layout()
        self.Show()


class LoginPanel(wx.Panel):

    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=SCREEN_SIZE,
                          style=wx.SIMPLE_BORDER)

        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(BACKGROUND_COLOR)

        # creating a vertical sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(int(SCREEN_HEIGT / 4))
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        label_font = wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        
        # adding username input 
        user_label = wx.StaticText(self, -1, label="Username:")
        user_label.SetForegroundColour(wx.BLACK)
        user_label.SetFont(label_font)
        self.user = wx.TextCtrl(self, -1, name="username", size=(200, -1))

        user_sizer.Add(user_label, 0, wx.ALL, 5)
        user_sizer.Add(self.user , 0, wx.ALL, 5)
        sizer.Add(user_sizer, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(int(SCREEN_HEIGT / 12))

        # adding password input 
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_label = wx.StaticText(self, 1, label="Password:")
        password_label.SetFont(label_font)
        self.password = wx.TextCtrl(self, -1, name="password", size=(200, -1))
        self.password.Bind(wx.EVT_BUTTON, self.on_login)

        password_sizer.Add(password_label, 0, wx.ALL, 5)
        password_sizer.Add(self.password, 0, wx.ALL, 5)
        sizer.Add(password_sizer, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(int(SCREEN_HEIGT / 12))

        # confirmation button
        buttonBox = wx.BoxSizer(wx.HORIZONTAL)

        button_login = wx.Button(self, label="Login")
        button_login.Bind(wx.EVT_BUTTON, self.on_login)

        buttonBox.Add(button_login, 1, wx.ALL, 5)
        
        sizer.Add(buttonBox, 0, wx.CENTER | wx.ALL, 5)

        # subscribe for login answer
        pub.subscribe(self.handle_login_answer, "login_answer")

        # arrange the frame
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_login_answer(self, answer):
        if answer == "ack":
            self.Hide()
            self.parent.control.Show()
        else:
            self.frame.SetStatusText("incorrect password or username")

    def on_login(self, event):

        if self.user and self.password:
            user = self.user.GetValue()
            password = self.password.GetValue()
            self.parent.user = user
            
            pub.sendMessage("login_request", username=user, password=password)
        else:
            self.frame.SetStatusText("please fill all inputs")


class ControlPanel(wx.Panel):

    OBJECT_RADIUS = 5
    FIELD_START_X = 50
    FIELD_END_X = 550
    FIELD_START_Y = 50
    FIELD_END_Y = 350
    FIELD_START_X_METERS = -3
    FIELD_END_X_METERS = 3
    FIELD_START_Y_METERS = -3
    FIELD_END_Y_METERS = 3

    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=SCREEN_SIZE,
                          style=wx.SIMPLE_BORDER)

        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(BACKGROUND_COLOR)

        # creating a vertical sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSpacer(int(SCREEN_WIDTH / 2))

        # setting the field painter
        self.paint_field()
        pub.subscribe(self.paint_cones, "cones_list")

        controls_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(controls_sizer, 0, wx.ALIGN_TOP)
        
        #creating directional buttons
        forwards_button = wx.Button(self, -1, "⬆", size=DIRECTION_BUTTON_SIZE)
        forwards_button.Bind(wx.EVT_BUTTON, self.on_forwards)
        right_button = wx.Button(self, -1, "⮕", size=DIRECTION_BUTTON_SIZE)
        right_button.Bind(wx.EVT_BUTTON, self.on_right)
        backwards_button = wx.Button(self, -1, "⬇", size=DIRECTION_BUTTON_SIZE)
        backwards_button.Bind(wx.EVT_BUTTON, self.on_backwards)
        left_button = wx.Button(self, -1, "⬅", size=DIRECTION_BUTTON_SIZE)
        left_button.Bind(wx.EVT_BUTTON, self.on_left)

        side_arrows_sizer = wx.BoxSizer(wx.HORIZONTAL)

        controls_sizer.Add(forwards_button, 0, wx.ALIGN_CENTER)
        controls_sizer.Add(side_arrows_sizer, 0, wx.ALIGN_CENTER)
        controls_sizer.Add(backwards_button, 0, wx.ALIGN_CENTER)

        side_arrows_sizer.Add(left_button, 0, wx.ALIGN_CENTER)
        side_arrows_sizer.Add(right_button, 0, wx.ALIGN_CENTER)

        #creating a timer for the direction "release"
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.stop)
        
        # arrange the frame
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def stop(self, event):
        pub.sendMessage("direction", direction="S")

    def on_forwards(self, event):
        pub.sendMessage("direction", direction="F")
        self.timer.Start(CLICK_LENGTH_MS, oneShot=True)

    def on_right(self, event):
        pub.sendMessage("direction", direction="R")
        self.timer.Start(CLICK_LENGTH_MS, oneShot=True)

    def on_backwards(self, event):
        pub.sendMessage("direction", direction="B")
        self.timer.Start(CLICK_LENGTH_MS, oneShot=True)

    def on_left(self, event):
        pub.sendMessage("direction", direction="L")
        self.timer.Start(CLICK_LENGTH_MS, oneShot=True)

    def paint_field(self):
        """set up the device context (DC) for painting"""
        self.dc = wx.ClientDC(self)
        self.dc.SetPen(wx.Pen("grey",style=wx.TRANSPARENT))
        self.dc.SetBrush(wx.Brush("grey", wx.SOLID))
        # set x, y, w, h for rectangle
        self.dc.DrawRectangle(self.FIELD_START_X, self.FIELD_START_Y, self.FIELD_END_X - self.FIELD_START_X,
                                        self.FIELD_END_Y - self.FIELD_START_Y)

    def paint_cones(self, cones: List[List[float]]):
        """
        draws a cone (yellow circle) on the screen
        :param x_list: all object x positions
        :param y_list: all object y positions
        :return:
        """

        self.paint_field()
        print(len(cones))
        for cone in cones:
            x, y = self._scale_to_field(*cone[:2])

            self.dc.SetPen(wx.Pen('black', 1))
            self.dc.SetBrush(wx.Brush('yellow'))
            self.dc.DrawCircle(x, y, self.OBJECT_RADIUS)

    def _scale_to_field(self, x: float, y: float) -> Tuple[int, int]:
        x = int(math_funcs.dead_band(x, (self.FIELD_START_X_METERS, self.FIELD_START_X), (self.FIELD_END_X_METERS, self.FIELD_END_X)))
        y = int(math_funcs.dead_band(y, (self.FIELD_START_Y_METERS, self.FIELD_START_Y), (self.FIELD_END_Y_METERS, self.FIELD_END_Y)))

        return x, y

if __name__ == "__main__":
    frame = MainFrame()
    app.MainLoop()