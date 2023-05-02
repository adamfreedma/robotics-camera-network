import wx
import wx.grid
import time
import threading
from pubsub import pub
from win32api import GetSystemMetrics
from typing import List, Tuple
import math_funcs

app = wx.App(False)

BACKGROUND_COLOR = (35, 35, 35, 255)
WIDGET_COLOR = (40, 40, 40, 255)
SCREEN_HEIGHT = GetSystemMetrics(1)
SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
DIRECTION_BUTTON_SIZE = (int(SCREEN_WIDTH / 16), int(SCREEN_HEIGHT / 16))
CLICK_LENGTH_MS = 500

LABEL_FONT = wx.Font(16, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL).Bold()
BUTTON_FONT = wx.Font(32, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL).Bold()


def create_text_ctrl(frame, name) -> wx.TextCtrl:
    text_ctrl = wx.TextCtrl(frame, -1, name=name, size=(200, -1), style=wx.TE_RICH)
    text_ctrl.SetBackgroundColour(WIDGET_COLOR)
    text_ctrl.SetForegroundColour(wx.WHITE)

    return text_ctrl


def create_label(frame, label) -> wx.StaticText:
    label = wx.StaticText(frame, -1, label=label)
    label.SetForegroundColour(wx.WHITE)
    label.SetFont(LABEL_FONT)

    return label


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
        
        # adding username input 
        user_label = create_label(self, "username:")
        self.user = create_text_ctrl(self, "username")

        user_sizer.Add(user_label, 0, wx.ALL, 5)
        user_sizer.Add(self.user, 0, wx.ALL, 5)

        sizer.Add(user_sizer, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(int(SCREEN_HEIGHT / 12))

        # adding password input 
        password_sizer = wx.BoxSizer(wx.HORIZONTAL)

        password_label = create_label(self, "password:")
        self.password = create_text_ctrl(self, "password")

        password_sizer.Add(password_label, 0, wx.ALL, 5)
        password_sizer.Add(self.password, 0, wx.ALL, 5)

        sizer.Add(password_sizer, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(int(SCREEN_HEIGHT / 12))

        # confirmation button
        confirm_button = wx.BoxSizer(wx.HORIZONTAL)

        login_button = wx.Button(self, label="Login")
        login_button.Bind(wx.EVT_BUTTON, self.on_login)

        login_button.SetBackgroundColour(WIDGET_COLOR)
        login_button.SetForegroundColour(wx.WHITE)

        confirm_button.Add(login_button, 1, wx.ALL, 5)
        
        sizer.Add(confirm_button, 0, wx.CENTER | wx.ALL, 5)

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
        
        # creating directional buttons
        self.forwards_button = wx.Button(self, -1, "⬆", size=DIRECTION_BUTTON_SIZE)
        self.forwards_button.Bind(wx.EVT_BUTTON, self.on_forwards)

        self.right_button = wx.Button(self, -1, "⮕", size=DIRECTION_BUTTON_SIZE)
        self.right_button.Bind(wx.EVT_BUTTON, self.on_right)

        self.backwards_button = wx.Button(self, -1, "⬇", size=DIRECTION_BUTTON_SIZE)
        self.backwards_button.Bind(wx.EVT_BUTTON, self.on_backwards)

        self.left_button = wx.Button(self, -1, "⬅", size=DIRECTION_BUTTON_SIZE)
        self.left_button.Bind(wx.EVT_BUTTON, self.on_left)

        # changing the button design
        self.forwards_button.SetBackgroundColour(WIDGET_COLOR)
        self.right_button.SetBackgroundColour(WIDGET_COLOR)
        self.backwards_button.SetBackgroundColour(WIDGET_COLOR)
        self.left_button.SetBackgroundColour(WIDGET_COLOR)

        self.forwards_button.SetForegroundColour(wx.WHITE)
        self.right_button.SetForegroundColour(wx.WHITE)
        self.left_button.SetForegroundColour(wx.WHITE)
        self.backwards_button.SetForegroundColour(wx.WHITE)

        side_arrows_sizer = wx.BoxSizer(wx.HORIZONTAL)

        side_arrows_sizer.Add(self.left_button, 0, wx.ALIGN_CENTER)
        side_arrows_sizer.Add(self.right_button, 0, wx.ALIGN_CENTER)
    
        controls_sizer.Add(self.forwards_button, 0, wx.ALIGN_CENTER)
        controls_sizer.Add(side_arrows_sizer, 0, wx.ALIGN_CENTER)
        controls_sizer.Add(self.backwards_button, 0, wx.ALIGN_CENTER)

        controls_sizer.AddSpacer(int(SCREEN_HEIGHT / 4))

        # creating a timer for the direction "release"
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.stop)
        
        # creating manager frame button
        manager_button = wx.Button(self, -1, "Manager", size=DIRECTION_BUTTON_SIZE)
        manager_button.Bind(wx.EVT_BUTTON, self.on_manager)

        manager_button.SetBackgroundColour(WIDGET_COLOR)
        manager_button.SetForegroundColour(wx.WHITE)
        
        controls_sizer.Add(manager_button, 0, wx.ALIGN_CENTER)
        
        # setting the field painter
        self.paint_field()
        pub.subscribe(self.paint_cones, "cones_list")
        
        # arrange the frame
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def stop(self, event):
        self.forwards_button.SetBackgroundColour(WIDGET_COLOR)
        self.right_button.SetBackgroundColour(WIDGET_COLOR)
        self.backwards_button.SetBackgroundColour(WIDGET_COLOR)
        self.left_button.SetBackgroundColour(WIDGET_COLOR)
        pub.sendMessage("direction", direction="S")

    def on_forwards(self, event):
        self.forwards_button.SetBackgroundColour(wx.WHITE)
        pub.sendMessage("direction", direction="F")
        self.timer.Start(CLICK_LENGTH_MS, oneShot=True)

    def on_right(self, event):
        self.right_button.SetBackgroundColour(wx.WHITE)
        pub.sendMessage("direction", direction="R")
        self.timer.Start(CLICK_LENGTH_MS, oneShot=True)

    def on_backwards(self, event):
        self.backwards_button.SetBackgroundColour(wx.WHITE)
        pub.sendMessage("direction", direction="B")
        self.timer.Start(CLICK_LENGTH_MS, oneShot=True)

    def on_left(self, event):
        self.left_button.SetBackgroundColour(wx.WHITE)
        pub.sendMessage("direction", direction="L")
        self.timer.Start(CLICK_LENGTH_MS, oneShot=True)
        
    def on_manager(self, event):
        self.Hide()
        self.parent.manager.Show()

    def paint_field(self):
        """set up the device context (DC) for painting"""
        self.dc = wx.ClientDC(self)
        self.dc.SetPen(wx.Pen("grey", style=wx.TRANSPARENT))
        self.dc.SetBrush(wx.Brush("grey", wx.SOLID))
        # set x, y, w, h for rectangle
        self.dc.DrawRectangle(self.FIELD_START_X, self.FIELD_START_Y, self.FIELD_END_X - self.FIELD_START_X,
                              self.FIELD_END_Y - self.FIELD_START_Y)

    def paint_cones(self, cones: List[List[float]]):
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

        sizer = wx.BoxSizer(wx.VERTICAL)

        back_button = wx.Button(self, label="⤺", size=(160, 80))
        back_button.Bind(wx.EVT_BUTTON, self.on_back)
        back_button.SetBackgroundColour((255, 0, 0, 200))
        back_button.SetForegroundColour((255, 255, 255, 200))
        back_button.SetFont(BUTTON_FONT)

        sizer.Add(back_button, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating a horizontal sizer to split users and cameras
        camera_users_sizer = wx.BoxSizer(wx.HORIZONTAL)
        camera_users_sizer.AddSpacer(int(SCREEN_WIDTH / 6))

        # creating a vertical sizer for the cameras
        self.cameras_sizer = wx.BoxSizer(wx.VERTICAL)

        camera_label = create_label(self, "camera list:")

        self.cameras_sizer.Add(camera_label, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        
        self.cameras_grid = wx.grid.Grid(self, size=(400, int(SCREEN_HEIGHT / 4)), style=wx.TE_RICH)
        self.cameras_grid.SetDefaultCellBackgroundColour(WIDGET_COLOR)
        self.cameras_grid.SetCellTextColour(wx.WHITE)
        self.cameras_grid.CreateGrid(0, 8)
        self.cameras_grid.SetColLabelValue(0, "camera")
        self.cameras_grid.SetColLabelValue(1, "mac")
        self.cameras_grid.SetColLabelValue(2, "x")
        self.cameras_grid.SetColLabelValue(3, "y")
        self.cameras_grid.SetColLabelValue(4, "z")
        self.cameras_grid.SetColLabelValue(5, "yaw")
        self.cameras_grid.SetColLabelValue(6, "pitch")
        self.cameras_grid.SetColLabelValue(7, "roll")

        self.cameras_sizer.Add(self.cameras_grid, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating a create camera form
        # adding name input
        name_label = create_label(self, "name:")
        self.name_input = create_text_ctrl(self, "name")

        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(name_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        name_sizer.Add(self.name_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.cameras_sizer.Add(name_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding password input
        mac_label = create_label(self, "mac:")
        self.mac_input = create_text_ctrl(self, "mac")

        mac_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mac_sizer.Add(mac_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        mac_sizer.Add(self.mac_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.cameras_sizer.Add(mac_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding x input
        x_label = create_label(self, "x:")
        self.x_input = create_text_ctrl(self, "x")

        x_sizer = wx.BoxSizer(wx.HORIZONTAL)
        x_sizer.Add(x_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        x_sizer.Add(self.x_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.cameras_sizer.Add(x_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding y input
        y_label = create_label(self, "y:")
        self.y_input = create_text_ctrl(self, "y")

        y_sizer = wx.BoxSizer(wx.HORIZONTAL)
        y_sizer.Add(y_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        y_sizer.Add(self.y_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.cameras_sizer.Add(y_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding z input
        z_label = create_label(self, "z:")
        self.z_input = create_text_ctrl(self, "z")

        z_sizer = wx.BoxSizer(wx.HORIZONTAL)
        z_sizer.Add(z_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        z_sizer.Add(self.z_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.cameras_sizer.Add(z_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding yaw input
        yaw_label = create_label(self, "yaw:")
        self.yaw_input = create_text_ctrl(self, "yaw")

        yaw_sizer = wx.BoxSizer(wx.HORIZONTAL)
        yaw_sizer.Add(yaw_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        yaw_sizer.Add(self.yaw_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.cameras_sizer.Add(yaw_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding pitch input
        pitch_label = create_label(self, "pitch:")
        self.pitch_input = create_text_ctrl(self, "pitch")

        pitch_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pitch_sizer.Add(pitch_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        pitch_sizer.Add(self.pitch_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.cameras_sizer.Add(pitch_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding roll input
        roll_label = create_label(self, "roll:")
        self.roll_input = create_text_ctrl(self, "roll")

        roll_sizer = wx.BoxSizer(wx.HORIZONTAL)
        roll_sizer.Add(roll_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        roll_sizer.Add(self.roll_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.cameras_sizer.Add(roll_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating the confirm button
        create_camera_button = wx.Button(self, label="+", size=(100, 100))
        create_camera_button.Bind(wx.EVT_BUTTON, self.on_create_camera)
        create_camera_button.SetForegroundColour((255, 255, 255, 200))
        create_camera_button.SetBackgroundColour((0, 255, 0, 200))
        create_camera_button.SetFont(BUTTON_FONT)

        edit_camera_button = wx.Button(self, label="✎", size=(100

                                                              , 100))
        edit_camera_button.Bind(wx.EVT_BUTTON, self.on_edit_camera)
        edit_camera_button.SetForegroundColour((255, 255, 255, 200))
        edit_camera_button.SetBackgroundColour((0, 0, 255, 200))
        edit_camera_button.SetFont(BUTTON_FONT)

        camera_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        camera_buttons_sizer.Add(create_camera_button, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        camera_buttons_sizer.Add(edit_camera_button, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.cameras_sizer.Add(camera_buttons_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        camera_users_sizer.Add(self.cameras_sizer, 0, wx.ALIGN_TOP | wx.ALL, 5)
        camera_users_sizer.AddSpacer(int(SCREEN_WIDTH / 3))

        # creating a vertical sizer for the users
        self.users_sizer = wx.BoxSizer(wx.VERTICAL)

        users_label = create_label(self, "users list:")
        
        self.users_sizer.Add(users_label, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating users grid
        self.users_grid = wx.grid.Grid(self, size=(250, int(SCREEN_HEIGHT / 4)))
        self.users_grid.SetDefaultCellBackgroundColour(WIDGET_COLOR)
        self.users_grid.SetCellTextColour(wx.WHITE)
        self.users_grid.CreateGrid(0, 2)
        self.users_grid.SetColLabelValue(0, "username")
        self.users_grid.SetColLabelValue(1, "hashed password")

        self.users_sizer.Add(self.users_grid, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating a create user form
        # adding username input
        username_label = create_label(self, "username:")
        self.username_input = create_text_ctrl(self, "username")

        username_sizer = wx.BoxSizer(wx.HORIZONTAL)
        username_sizer.Add(username_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        username_sizer.Add(self.username_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.users_sizer.Add(username_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # adding password input
        password_label = create_label(self, "password:")
        self.password_input = create_text_ctrl(self, "password")

        password_sizer = wx.BoxSizer(wx.HORIZONTAL)
        password_sizer.Add(password_label, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        password_sizer.Add(self.password_input, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.users_sizer.Add(password_sizer, 0,  wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # creating the create and edit buttons
        create_user_button = wx.Button(self, label="+", size=(100, 100))
        create_user_button.Bind(wx.EVT_BUTTON, self.on_create_user)
        create_user_button.SetForegroundColour((255, 255, 255, 200))
        create_user_button.SetBackgroundColour((0, 255, 0, 200))
        create_user_button.SetFont(BUTTON_FONT)

        edit_user_button = wx.Button(self, label="✎", size=(100, 100))
        edit_user_button.Bind(wx.EVT_BUTTON, self.on_edit_user)
        edit_user_button.SetForegroundColour((255, 255, 255, 200))
        edit_user_button.SetBackgroundColour((0, 0, 255, 200))
        edit_user_button.SetFont(BUTTON_FONT)

        user_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        user_buttons_sizer.Add(create_user_button, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)
        user_buttons_sizer.Add(edit_user_button, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        self.users_sizer.Add(user_buttons_sizer, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        camera_users_sizer.Add(self.users_sizer, 0, wx.ALIGN_TOP | wx.ALL, 5)

        sizer.Add(camera_users_sizer, 0, wx.ALIGN_TOP | wx.ALL, 5)

        delete_button = wx.Button(self, label="🗑", size=(200, 100))
        delete_button.Bind(wx.EVT_BUTTON, self.on_delete)
        delete_button.SetBackgroundColour((255, 0, 0, 200))
        delete_button.SetForegroundColour((255, 255, 255, 200))
        delete_button.SetFont(BUTTON_FONT)

        sizer.Add(delete_button, 0, wx.ALIGN_TOP | wx.ALIGN_CENTER, 5)

        # subscribe for list refreshes        
        pub.subscribe(self.handle_users_refresh, "users_list")
        pub.subscribe(self.handle_cameras_refresh, "cameras_list")
        # subscribe for creation answers
        pub.subscribe(self.handle_create_user_answer, "create_user_answer")
        pub.subscribe(self.handle_create_camera_answer, "create_camera_answer")
        # subscribe for edit answers
        pub.subscribe(self.handle_edit_user_answer, "edit_user_answer")
        pub.subscribe(self.handle_edit_camera_answer, "edit_camera_answer")
        
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
        x = self.x_input.GetValue()
        self.x_input.Clear()
        y = self.y_input.GetValue()
        self.y_input.Clear()
        z = self.z_input.GetValue()
        self.z_input.Clear()
        yaw = self.yaw_input.GetValue()
        self.yaw_input.Clear()
        pitch = self.pitch_input.GetValue()
        self.pitch_input.Clear()
        roll = self.roll_input.GetValue()
        self.roll_input.Clear()

        if name and mac:
            pub.sendMessage("create_camera", name=name, mac=mac, x=x, y=y, z=z, yaw=yaw, pitch=pitch, roll=roll)
        else:
            self.frame.SetStatusText("please fill all fields!")

    def on_edit_camera(self, event):
        name = self.name_input.GetValue()
        self.name_input.Clear()
        mac = self.mac_input.GetValue()
        self.mac_input.Clear()
        x = self.x_input.GetValue()
        self.x_input.Clear()
        y = self.y_input.GetValue()
        self.y_input.Clear()
        z = self.z_input.GetValue()
        self.z_input.Clear()
        yaw = self.yaw_input.GetValue()
        self.yaw_input.Clear()
        pitch = self.pitch_input.GetValue()
        self.pitch_input.Clear()
        roll = self.roll_input.GetValue()
        self.roll_input.Clear()

        if name and mac:
            pub.sendMessage("edit_camera", name=name, mac=mac, x=x, y=y, z=z, yaw=yaw, pitch=pitch, roll=roll)
        else:
            self.frame.SetStatusText("please fill all fields!")

    def on_create_user(self, event):
        username = self.username_input.GetValue()
        self.username_input.Clear()
        password = self.password_input.GetValue()
        self.password_input.Clear()

        if username and password:
            pub.sendMessage("create_user", username=username, password=password)
        else:
            self.frame.SetStatusText("please fill both username and password fields!")

    def on_edit_user(self, event):
        username = self.username_input.GetValue()
        self.username_input.Clear()
        password = self.password_input.GetValue()
        self.password_input.Clear()

        if username and password:
            pub.sendMessage("edit_user", username=username, password=password)
        else:
            self.frame.SetStatusText("please fill both username and password fields!")

    def handle_cameras_refresh(self, cameras_list):
        if self.cameras_grid.GetNumberRows():
            self.cameras_grid.DeleteRows(numRows=self.cameras_grid.GetNumberRows())
        self.cameras_grid.InsertRows(numRows=len(cameras_list))

        grid_width = 8

        for i in range(len(cameras_list)):
            for j in range(grid_width):
                # inserting cell value
                self.cameras_grid.SetCellValue(i, j, str(cameras_list[i][j+1]))
                # setting cell to read only
                self.cameras_grid.SetReadOnly(i, j)

    def handle_users_refresh(self, users_list):
        if self.users_grid.GetNumberRows():
            self.users_grid.DeleteRows(numRows=self.users_grid.GetNumberRows())
        self.users_grid.InsertRows(numRows=len(users_list))

        grid_width = 2

        for i in range(len(users_list)):
            for j in range(grid_width):
                # inserting cell value
                self.users_grid.SetCellValue(i, j, str(users_list[i][j+1]))
                # setting cell to read only
                self.users_grid.SetReadOnly(i, j)

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

    def handle_edit_user_answer(self, answer):

        if answer == "S":
            self.refresh_lists()
        else:
            self.frame.SetStatusText("username dose not exists, try another one")

    def handle_edit_camera_answer(self, answer):

        if answer == "S":
            self.refresh_lists()
        else:
            self.frame.SetStatusText("mac does not exist, try another one")

    @staticmethod
    def refresh_lists():
        pub.sendMessage("refresh_request")


if __name__ == "__main__":
    frame = MainFrame()
    app.MainLoop()
