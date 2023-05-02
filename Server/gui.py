import wx
import wx.grid
import time
import threading
from pubsub import pub
from win32api import GetSystemMetrics
from typing import List, Tuple
import math_funcs

app = wx.App(False)

BACKGROUND_COLOR = wx.LIGHT_GREY
SCREEN_HEIGHT = GetSystemMetrics(1)
SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
DIRECTION_BUTTON_SIZE = (int(SCREEN_WIDTH / 16), int(SCREEN_HEIGHT / 16))
CLICK_LENGTH_MS = 500

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
        self.manager = ManagerPanel(self, self.frame)

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
        sizer.AddSpacer(int(SCREEN_HEIGHT / 4))
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.label_font = wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        
        # adding username input 
        user_label = wx.StaticText(self, -1, label="Username:")
        user_label.SetForegroundColour(wx.BLACK)
        user_label.SetFont(self.label_font)
        self.user = wx.TextCtrl(self, -1, name="username", size=(200, -1))

        user_sizer.Add(user_label, 0, wx.ALL, 5)
        user_sizer.Add(self.user , 0, wx.ALL, 5)
        sizer.Add(user_sizer, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(int(SCREEN_HEIGHT / 12))

        # adding password input 
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_label = wx.StaticText(self, 1, label="Password:")
        password_label.SetFont(self.label_font)
        self.password = wx.TextCtrl(self, -1, name="password", size=(200, -1))

        password_sizer.Add(password_label, 0, wx.ALL, 5)
        password_sizer.Add(self.password, 0, wx.ALL, 5)
        sizer.Add(password_sizer, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(int(SCREEN_HEIGHT / 12))

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

        side_arrows_sizer.Add(left_button, 0, wx.ALIGN_CENTER)
        side_arrows_sizer.Add(right_button, 0, wx.ALIGN_CENTER)
    
        controls_sizer.Add(forwards_button, 0, wx.ALIGN_CENTER)
        controls_sizer.Add(side_arrows_sizer, 0, wx.ALIGN_CENTER)
        controls_sizer.Add(backwards_button, 0, wx.ALIGN_CENTER)

        
        controls_sizer.AddSpacer(int(SCREEN_HEIGHT / 4))

        #creating a timer for the direction "release"
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.stop)
        
        # creating manager frame button
        manager_button = wx.Button(self, -1, "Manager", size=DIRECTION_BUTTON_SIZE)
        manager_button.Bind(wx.EVT_BUTTON, self.on_manager)
        
        controls_sizer.Add(manager_button, 0, wx.ALIGN_CENTER)
        
        # setting the field painter
        self.paint_field()
        pub.subscribe(self.paint_cones, "cones_list")
        
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
        
    def on_manager(self, event):
        self.Hide()
        self.parent.manager.Show()

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
        for cone in cones:
            x, y = self._scale_to_field(*cone[:2])

            self.dc.SetPen(wx.Pen('black', 1))
            self.dc.SetBrush(wx.Brush('yellow'))
            self.dc.DrawCircle(x, y, self.OBJECT_RADIUS)

    def _scale_to_field(self, x: float, y: float) -> Tuple[int, int]:
        x = int(math_funcs.dead_band(x, (self.FIELD_START_X_METERS, self.FIELD_START_X), (self.FIELD_END_X_METERS, self.FIELD_END_X)))
        y = int(math_funcs.dead_band(y, (self.FIELD_START_Y_METERS, self.FIELD_START_Y), (self.FIELD_END_Y_METERS, self.FIELD_END_Y)))

        return x, y


class ManagerPanel(wx.Panel):

    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=SCREEN_SIZE,
                          style=wx.SIMPLE_BORDER)

        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(BACKGROUND_COLOR)

        self.label_font = wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.button_font = wx.Font(32, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        sizer = wx.BoxSizer(wx.VERTICAL)

        back_button = wx.Button(self, label="<-", size=(160, 80))
        back_button.Bind(wx.EVT_BUTTON, self.on_back)
        back_button.SetBackgroundColour((255, 0, 0, 200))
        back_button.SetForegroundColour((255, 255, 255, 200))
        back_button.SetFont(self.button_font)

        sizer.Add(back_button, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating a hotizontal sizer to split users and cameras
        camera_users_sizer = wx.BoxSizer(wx.HORIZONTAL)
        camera_users_sizer.AddSpacer(int(SCREEN_WIDTH / 5))

        # creating a vertical sizer for the cameras
        self.cameras_sizer = wx.BoxSizer(wx.VERTICAL)
        self.cameras_sizer.AddSpacer(int(SCREEN_HEIGHT / 8))

        camera_label = wx.StaticText(self, -1, label="camera list:")
        camera_label.SetForegroundColour(wx.BLACK)
        camera_label.SetFont(self.label_font)

        self.cameras_sizer.Add(camera_label, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        
        self.cameras_grid = wx.grid.Grid(self, size=(250, int(SCREEN_HEIGHT / 3)))
        self.cameras_grid.CreateGrid(0, 2)
        self.cameras_grid.SetColLabelValue(0, "camera")
        self.cameras_grid.SetColLabelValue(1, "mac")

        self.cameras_sizer.Add(self.cameras_grid, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating a create camera form
        # adding name input
        name_label = wx.StaticText(self, -1, label="Name:")
        name_label.SetForegroundColour(wx.BLACK)
        name_label.SetFont(self.label_font)
        self.name_input = wx.TextCtrl(self, -1, name="name", size=(200, -1))

        self.cameras_sizer.Add(name_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        self.cameras_sizer.Add(self.name_input, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding password input
        mac_label = wx.StaticText(self, 1, label="Mac:")
        mac_label.SetForegroundColour(wx.BLACK)
        mac_label.SetFont(self.label_font)
        self.mac_input = wx.TextCtrl(self, -1, name="mac", size=(200, -1))

        self.cameras_sizer.Add(mac_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        self.cameras_sizer.Add(self.mac_input, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating the confirm button
        create_camera_button = wx.Button(self, label="+", size=(200, 100))
        create_camera_button.Bind(wx.EVT_BUTTON, self.on_create_camera)
        create_camera_button.SetForegroundColour((255, 255, 255, 200))
        create_camera_button.SetBackgroundColour((0, 255, 0, 200))
        create_camera_button.SetFont(self.button_font)

        self.cameras_sizer.Add(create_camera_button, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        camera_users_sizer.Add(self.cameras_sizer, 0, wx.ALIGN_TOP | wx.ALL, 5)
        camera_users_sizer.AddSpacer(int(SCREEN_WIDTH / 3))

        # creating a vertical sizer for the users
        self.users_sizer = wx.BoxSizer(wx.VERTICAL)
        self.users_sizer.AddSpacer(int(SCREEN_HEIGHT / 8))
        
        users_label = wx.StaticText(self, 1, label="users list:")
        users_label.SetForegroundColour(wx.BLACK)
        users_label.SetFont(self.label_font)
        
        self.users_sizer.Add(users_label, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating users grid
        self.users_grid = wx.grid.Grid(self, size=(250, int(SCREEN_HEIGHT / 3)))
        self.users_grid.CreateGrid(0, 2)
        self.users_grid.SetColLabelValue(0, "username")
        self.users_grid.SetColLabelValue(1, "hashed password")

        self.users_sizer.Add(self.users_grid, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating a create user form
        # adding username input
        user_label = wx.StaticText(self, -1, label="Username:")
        user_label.SetForegroundColour(wx.BLACK)
        user_label.SetFont(self.label_font)
        self.username_input = wx.TextCtrl(self, -1, name="username", size=(200, -1))

        self.users_sizer.Add(user_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        self.users_sizer.Add(self.username_input, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding password input
        password_label = wx.StaticText(self, 1, label="Password:")
        password_label.SetForegroundColour(wx.BLACK)
        password_label.SetFont(self.label_font)
        self.password_input = wx.TextCtrl(self, -1, name="password", size=(200, -1))

        self.users_sizer.Add(password_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        self.users_sizer.Add(self.password_input, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating the confirm button
        create_user_button = wx.Button(self, label="+", size=(200, 100))
        create_user_button.Bind(wx.EVT_BUTTON, self.on_create_user)
        create_user_button.SetForegroundColour((255, 255, 255, 200))
        create_user_button.SetBackgroundColour((0, 255, 0, 200))
        create_user_button.SetFont(self.button_font)

        self.users_sizer.Add(create_user_button, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        camera_users_sizer.Add(self.users_sizer, 0, wx.ALIGN_TOP | wx.ALL, 5)

        sizer.Add(camera_users_sizer, 0, wx.ALIGN_TOP | wx.ALL, 5)

        delete_button = wx.Button(self, label="🗑", size=(200, 100))
        delete_button.Bind(wx.EVT_BUTTON, self.on_delete)
        delete_button.SetBackgroundColour((255, 0, 0, 200))
        delete_button.SetForegroundColour((255, 255, 255, 200))
        delete_button.SetFont(self.button_font)

        sizer.Add(delete_button, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # subscribe for list refreshes        
        pub.subscribe(self.handle_users_refresh, "users_list")
        pub.subscribe(self.handle_cameras_refresh, "cameras_list")
        # subscribe for creation answers
        pub.subscribe(self.handle_create_user_answer, "create_user_answer")
        pub.subscribe(self.handle_create_camera_answer, "create_camera_answer")
        
        self.refresh_lists()

        # arrange the frame
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def on_back(self, event):
        self.Hide()
        self.parent.control.Show()

    def on_delete(self, event):
        selected_rows = self.cameras_grid.GetSelectedRows()
        if len(self.cameras_grid.GetSelectionBlockTopLeft()):
            selected_cell_rows = range(self.cameras_grid.GetSelectionBlockTopLeft()[0][0],
                                       self.cameras_grid.GetSelectionBlockBottomRight()[0][0]+1)
        else:
            selected_cell_rows = []

        selected_cameras = list(set(selected_rows) | set(selected_cell_rows))

        for camera_row in selected_cameras:
            print(camera_row, self.cameras_grid.GetCellValue(camera_row, 1))
            pub.sendMessage("delete_camera", mac=self.cameras_grid.GetCellValue(camera_row, 1))

        selected_rows = self.users_grid.GetSelectedRows()
        if len(self.users_grid.GetSelectionBlockTopLeft()):
            selected_cell_rows = range(self.users_grid.GetSelectionBlockTopLeft()[0][0],
                                       self.users_grid.GetSelectionBlockBottomRight()[0][0]+1)
        else:
            selected_cell_rows = []

        selected_users = list(set(selected_rows) | set(selected_cell_rows))

        if len(selected_users) >= self.users_grid.GetNumberRows():
            self.frame.SetStatusText("You may not delete all users.")
        else:
            for user_row in selected_users:
                pub.sendMessage("delete_user", username=self.users_grid.GetCellValue(user_row, 0))

            self.refresh_lists()

    def on_create_camera(self, event):
        name = self.name_input.GetValue()
        self.name_input.Clear()
        mac = self.mac_input.GetValue()
        self.mac_input.Clear()

        if name and mac:
            pub.sendMessage("create_camera", name=name, mac=mac)
        else:
            self.frame.SetStatusText("please fill both name and mac fields!")

    def on_create_user(self, event):
        username = self.username_input.GetValue()
        self.username_input.Clear()
        password = self.password_input.GetValue()
        self.password_input.Clear()

        if username and password:
            pub.sendMessage("create_user", username=username, password=password)
        else:
            self.frame.SetStatusText("please fill both username and password fields!")

    def handle_cameras_refresh(self, cameras_list):
        if self.cameras_grid.GetNumberRows():
            self.cameras_grid.DeleteRows(numRows=self.cameras_grid.GetNumberRows())
        self.cameras_grid.InsertRows(numRows=len(cameras_list))

        for i in range(len(cameras_list)):
            # inserting cell values
            self.cameras_grid.SetCellValue(i, 0, cameras_list[i][1])
            self.cameras_grid.SetCellValue(i, 1, cameras_list[i][2])
            # setting cells to read only
            self.cameras_grid.SetReadOnly(i, 0)
            self.cameras_grid.SetReadOnly(i, 1)

    def handle_users_refresh(self, users_list):
        if self.users_grid.GetNumberRows():
            self.users_grid.DeleteRows(numRows=self.users_grid.GetNumberRows())
        self.users_grid.InsertRows(numRows=len(users_list))

        for i in range(len(users_list)):
            # inserting cell values
            self.users_grid.SetCellValue(i, 0, users_list[i][1])
            self.users_grid.SetCellValue(i, 1, users_list[i][2])
            # setting cells to read only
            self.users_grid.SetReadOnly(i, 0)
            self.users_grid.SetReadOnly(i, 1)

    def handle_create_user_answer(self, answer):

        if answer == "S":
            self.refresh_lists()
        else:
            self.frame.SetStatusText("username already exists, try another one")

    def handle_create_camera_answer(self, answer):

        if answer == "S":
            self.refresh_lists()
        else:
            self.frame.SetStatusText("mac or name already exists, try another one")

    @staticmethod
    def refresh_lists():
        pub.sendMessage("refresh_request")


if __name__ == "__main__":
    frame = MainFrame()
    app.MainLoop()
