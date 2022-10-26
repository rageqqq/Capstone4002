
from queue import Queue
import numpy as np


class activity:
    """IMU readings buffer of size 60 (3s)

    activity class holds a sliding window of size 60 and tracks the y acceleration of the readings in the window.

    Attributes:
        window: A fifo queue that acts as the sliding window currently tracked.
        activity_level: An integer count of the number of readings above activity_threshold.
        counter: An integer count of number of readings since last time window was extracted. 0 means windows is available to be extracted.
        activity_threshold: An integer value denoting the activity level of intrest for a window to be extracted/action to be detected.
    """

    def __init__(self):
        self.window = []
        self.activity_level = 0
        self.activity_threshold = 38
        self.window_size = 60
        self.cooldown = 0
        self.cooldown_window = 90

    def init_window(self):
        self.window = []

    def put(self, data):
        """Inserts data into the window.

        Reading data is inserted into the sliding window, removing the oldest value if size is > 60 (3s).
        counter is incremented if window is not ready for extracted or set to 0 if it is(60 readings since last extraction).

        Args:
            data (list): readings obtained from imu of shape (6,)

        """
        if self.cooldown>0:
            self.cooldown -=1
        if len(self.window) == self.window_size:
            removed = self.window.pop(0)
            if removed[0] > 0.7:
                self.activity_level -= 1
            if removed[0] > 0.5:
                self.activity_level -= 1
            if removed[0] > 0:
                self.activity_level -= 2
            if removed[0] > -0.2:
                self.activity_level -= 1

        if data[0] > 0.7:
            self.activity_level += 1
        if data[0] > 0.5:
            self.activity_level += 1
        if data[0] > 0:
            self.activity_level += 2
        if data[0] > -0.2:
            self.activity_level += 1




        self.window.append(data)

    def extract_window(self):
        """Extract the currently held sliding window in window.

        window of size 60 is extracted if counter = 0 indicating more than 60 readings since last extraction.
        Output is in the form [Acc_x, Acc_y, Acc_z, Gyro_x, Gyro_y, Gyro_z] * 60

        Returns:
            list: list of the readings in window of shape (60,6)

        """
        
        if len(self.window) < self.window_size:
            return
        elif self.cooldown!= 0:
            return

        # If current tracked activity level is greater than threshold, trigger classification
        
        elif self.activity_level > self.activity_threshold:
            self.cooldown = self.cooldown_window
            #print(self.activity_level)

            out = []

            for i in range(self.window_size):
                temp_data = self.window.pop(0)
                out_format = [temp_data[0], temp_data[1], temp_data[2],
                              temp_data[3], temp_data[4], temp_data[5]]
                out.append(out_format)
            self.activity_level = 0

            #output = [np.array(acc_x) + np.array(acc_y) + np.array(acc_z) + np.array(gyro_x) + np.array(gyro_y) + np.array(gyro_z)]
            return out

    # If not ready and not threshold, return null. Else return flat array

    def update(self, data):
        """Updates currently monitored sliding window

        Updates data held in window buffer with reading from current time step.
        Returns window if action is detected in sliding window

        Args:
            data (list): readings obtained from imu of shape (6,)

        Returns:
            list: list of the readings in window of shape (60,6) if action is detected
            None: None if no action is detected

        """
        self.put(data)
        return self.extract_window()

    def a_level(self):
        return(self.activity_level)
