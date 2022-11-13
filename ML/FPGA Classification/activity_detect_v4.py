
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
        self.activity_threshold = 45
        self.window_size = 60
        self.sliding_window = 65
        self.cooldown = 0
        self.cooldown_window = 70
        self.trigger_counter = 0

    def init_window(self):
        self.window = []

    def put(self, data):
        """Inserts data into the window.

        Reading data is inserted into the sliding window, removing the oldest value if size is > 90 (4.5s).
        cooldown is decremented when window is not ready for extracted or set to 60 if it is(60 readings since last extraction).
        Activity value is increased based on x axis thresholds(vertical acceleration)


        Args:
            data (list): readings obtained from imu of shape (6,)

        """

        #Take a larger window, oversample by x samples after hitting threshold. return 5 60 size windows, run classification 5 times and take the mode.
        #Hit threshold, increment counter, wait for 5 more readings, once counter hit 5, return the last 5 60 sized windows
        if self.cooldown>0:
            self.cooldown -=1

       
        #print(data[0])
        if (len(self.window) > 5):
            if data[0] > -0.3 and data[0] > self.window[-1][0]:
                self.activity_level += 2
                if self.window[-2][0] > 0.7 and self.window[-1][0] > self.window[-2][0]:
                     self.activity_level += .5
                if (abs(data[0] - self.window[-1][0])<0.1) and data[0]<0.5:
                    self.activity_level += 2
            if data[0] > 1.2:
                self.activity_level += 3
            elif data[0] > 0.98:
                self.activity_level += 1
            elif data[0] > 0.8:
                self.activity_level += 1
            elif data[0] > 0.6:
                self.activity_level += 1
            elif data[0] > 0.5:
                self.activity_level += 1
            elif data[0] > 0.25:
                self.activity_level += 1
            elif data[0] > 0:
                self.activity_level += 3
            elif data[0] > -0.2:
                self.activity_level += 1
            elif data[0] > -0.3:
                self.activity_level += 1

            

        
        if (len(self.window) == self.sliding_window):
            if self.window[5][0] > -0.3 and self.window[5][0] > self.window[4][0]:
                self.activity_level -= 2
                if self.window[3][0] > 0.7 and self.window[4][0] > self.window[3][0]:
                     self.activity_level -= .5
                if (abs(self.window[5][0] - self.window[4][0])<0.1) and self.window[5][0] < 0.5:
                    self.activity_level -= 2
            if self.window[5][0] > 1.2:
                self.activity_level -= 3    
            elif self.window[5][0] > 0.98:
                self.activity_level -= 1
            elif self.window[5][0] > 0.8:
                self.activity_level -= 1
            elif self.window[5][0] > 0.6:
                self.activity_level -= 1
            elif self.window[5][0] > 0.5:
                self.activity_level -= 1
            elif self.window[5][0] > 0.25:
                self.activity_level -= 1
            elif self.window[5][0] > 0:
                self.activity_level -= 3
            elif self.window[5][0] > -0.2:
                self.activity_level -= 1
            elif self.window[5][0] > -0.3:
                self.activity_level -= 1

            self.window.pop(0)
            #print(self.activity_level)

            if self.activity_level<0:
                self.activity_level = 0
                raise Exception("Negative Activity")



        self.window.append(data)
        if (len(self.window)>65):
            raise Exception("Expanded window")

        

    def extract_window(self):
        """Extract the currently held sliding window in window.

        window of size 60 is extracted if counter = 0 indicating more than 60 readings since last extraction.
        Output is in the form [Acc_x, Acc_y, Acc_z, Gyro_x, Gyro_y, Gyro_z] * 60

        Returns:
            list: list of the readings in window of shape (60,6)

        """
        
        if len(self.window) < self.sliding_window:
            return
        elif self.cooldown!= 0:
            return

        # If current tracked activity level is greater than threshold, trigger classification
        
        elif self.activity_level > self.activity_threshold and self.trigger_counter == 0:
            self.trigger_counter = 1
        elif 0 < self.trigger_counter < 5:
            self.trigger_counter+=1


        if self.trigger_counter < 5:
            return
        else:

            self.cooldown = self.cooldown_window
            
            #set coooldown, take 60-79, 19-79, 18-78, 17-77, 16-76

            out = (self.window[5:65], self.window[4:64], self.window[3:63])
            #print(len(out[0]), len(out[1]), len(out[2]), len(out[3]), len(out[4]))

            self.trigger_counter = 0
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


    def reset(self):
        self.window = []
        self.activity_level = 0
        self.activity_threshold = 55
        self.window_size = 60
        self.sliding_window = 65
        self.cooldown = 0
        self.cooldown_window = 65
        self.trigger_counter = 0