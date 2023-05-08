import networktables
from typing import Any, Tuple


class RobotConnection:

    TEAM_NUMBER = 1690
    TABLE_NAME = "CameraNetwork"
    X_ENTRY_NAME = "ConePositionX"
    Y_ENTRY_NAME = "ConePositionY"
    DIRECTION_ENTRY_NAME = "Direction"

    def __init__(self):

        self.nt_instance = networktables.NetworkTablesInstance.getDefault()
        self._connect()

    def _connect(self):
        """
        conencts to the robot using networktables
        """
        self.nt_instance.startClientTeam(self.TEAM_NUMBER)
        self.nt_instance.startDSClient()

        self.camera_network_table = self.nt_instance.getTable(self.TABLE_NAME)
        self.cone_position_x_entry = self.camera_network_table.getEntry(self.X_ENTRY_NAME)
        self.cone_position_y_entry = self.camera_network_table.getEntry(self.Y_ENTRY_NAME)
        self.direction_entry = self.camera_network_table.getEntry(self.DIRECTION_ENTRY_NAME)

    @staticmethod
    def _update(data: Any, entry: networktables.NetworkTableEntry):
        """
        updates a value
        :param data: data to set
        :param entry: which entry to set
        """
        entry.setValue(data)

    def update_cone(self, cone: Tuple[float, float]):
        """
        updates cones data
        :param cone: the cone location
        """
        self._update(cone[0], self.cone_position_x_entry)
        self._update(cone[1], self.cone_position_y_entry)

    def update_direction(self, direction: str):
        """
        updates moving direction
        :param direction: the direction to move
        """
        self._update(direction, self.direction_entry)
