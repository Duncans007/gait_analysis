import numpy as np
from scipy import interpolate

# Selection of Kalman filter classes for IMU analysis

# class kalman_filter_6dof() for fusing gyroscope and accelerometer into roll and pitch
# class kalman_filter_velocity() for fusing position and acceleration into walking speed


class kalman_filter_6dof():

    # Kalman Filter for 6DoF IMU Sensor Fusion
    # Fuses gyroscope and accelerometer measurements for pitch and roll angles
    # Applicable to any IMU sensor

    # Functions:
    # __init__(): Contains Q and R arrays for modifying filter behaviour
    # reset(): Sets any changing variables to 0 for a new dataset to be processed
    # update(accelerometer, position, pitch, dt): Adds new values to filter and updates prediction
    # analyze_dataset(dataset): Iterates through data to post-process a complete dataset
    # zero(signal): Uses seconds 2-4 of given signal to compute offset that is applied to the entire signal
    # smooth(input_arr, time_arr): Smooths curve

    # Usage:
    # Creating object:
    #   6d_filter = kalman_filter_6dof()
    # Modifying Q and R coefficients:
    #   6d_filter.Q_coeff = 0.0001
    # Using for Live Filtering (manual update):
    #   roll, pitch = 6d_filter.update([gy_x, gy_y, gy_z], [ac_x, ac_y, ac_z], sample_time)
    # Using for Post-Processing:
    #   roll_over_time, pitch_over_time = v_filter.analyze_dataset(dataset)
    #   Where dataset contains 7 sub-arrays for [time, gy_x, gy_y, gy_z, ac_x, ac_y, ac_z]

    def __init__(self):
        self.reset()

        # Modifiable coefficient arrays
        self.Q = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]]) * .000001

        self.R = np.array([[1, 0],
                           [0, 10]]) * 0.001

        # Variable Initializations
        self.C = np.array([[1, 0, 0, 0],
                           [0, 0, 1, 0]])

    def reset(self):
        # Reset changing states of the object before starting a new analysis

        self.x = np.transpose(np.array([[0, 0, 0, 0]]))

        self.P = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])

        self.acc_x = [0, 0]
        self.acc_y = [0, 0]
        self.acc_z = [0, 0]

    def analyze_dataset(self, dataset):
        # Takes in complete set of data (time and 6DoF sensor values) and outputs angles over time.

        # Dataset is an array with 7 sub-arrays:
        time_arr = dataset[0]  # Time array for dataset

        gy_x = dataset[1]
        gy_y = dataset[2]
        gy_z = dataset[3]

        ac_x = dataset[4]
        ac_y = dataset[5]
        ac_z = dataset[6]

        self.reset()
        roll_arr = [0]
        pitch_arr = [0]
        for i in range(1, len(time_arr)):
            dt = time_arr[i] - time_arr[i - 1]
            roll, pitch = self.update([gy_x[i], gy_y[i], gy_z[i]], [ac_x[i], ac_y[i], ac_z[i]], dt)
            roll_arr.append(roll)
            pitch_arr.append(pitch)

        roll_arr = self.zero(roll_arr)
        pitch_arr = self.zero(pitch_arr)

        roll_arr = self.smooth(roll_arr, time_arr, smooth_coeff=1)
        pitch_arr = self.smooth(pitch_arr, time_arr, smooth_coeff=1)

        return roll_arr, pitch_arr

    def update(self, gyroscope, accelerometer, dt):
        # Used to update state of object with new values
        # Returns roll and pitch and updates system
        # Unpack inputs
        self.acc_x.append(accelerometer[0])
        self.acc_y.append(accelerometer[1])
        self.acc_z.append(accelerometer[2])
        self.acc_x.pop(0)
        self.acc_y.pop(0)
        self.acc_z.pop(0)
        acc_x_mean = np.mean(self.acc_x)
        acc_y_mean = np.mean(self.acc_y)
        acc_z_mean = np.mean(self.acc_z)

        gyro_x = np.radians(gyroscope[0])
        gyro_y = np.radians(gyroscope[1])
        gyro_z = np.radians(gyroscope[2])
        roll_current = self.x[0][0]
        pitch_current = self.x[2][0]

        # Calculate accelerometer angles
        accel_roll = np.arctan2(acc_z_mean, np.sqrt((acc_y_mean * acc_y_mean) + (acc_x_mean * acc_x_mean)))
        accel_pitch = np.arctan2(-acc_x_mean, np.sqrt((acc_z_mean * acc_z_mean) + (acc_y_mean * acc_y_mean)))

        # Get euler angle derivatives of input gyroscope values
        roll_dot = gyro_x \
                   + (np.sin(roll_current) * np.tan(pitch_current) * gyro_z) \
                   + (np.cos(roll_current) * np.tan(pitch_current) * gyro_y)
        pitch_dot = np.cos(roll_current) * gyro_z - np.sin(roll_current) * gyro_y

        # Calculate A and B arrays based on time step
        A = np.array([[1, -dt, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1, -dt],
                      [0, 0, 0, 1]])

        B = np.array([[dt, 0],
                      [0, 0],
                      [0, dt],
                      [0, 0]])

        # Assemble input matrices
        measured_input = np.transpose(np.array([[roll_dot, pitch_dot]]))
        acceleration_estimates = np.transpose(np.array([[accel_roll, accel_pitch]]))

        # Prediction equations
        x_new = (A.dot(self.x)) + (B.dot(measured_input))
        self.P = A.dot(self.P.dot(np.transpose(A))) + self.Q

        # Update equations
        y_new = acceleration_estimates - self.C.dot(x_new)
        S = self.C.dot(self.P.dot(np.transpose(self.C))) + self.R
        K = self.P.dot(np.transpose(self.C).dot(np.linalg.inv(S)))
        x_new = x_new + K.dot(y_new)

        self.x = x_new
        self.P = (np.eye(4) - K.dot(self.C)).dot(self.P)

        return np.degrees(self.x[0][0]), np.degrees(self.x[2][0])

    def zero(self, arr):
        # Zeroes input function based on seconds 2-4 of data
        calib_val = np.mean(arr[100:200])
        output = [x - calib_val for x in arr]
        return output

    def smooth(self, arr_to_smooth, time_arr, smooth_coeff=1):
        # Smooths input function using a univariate spline
        smoothed_arr = interpolate.UnivariateSpline(time_arr, arr_to_smooth, s=smooth_coeff)
        smoothed_arr = smoothed_arr(time_arr)
        return smoothed_arr


class kalman_filter_velocity():
    # Kalman Filter for Velocity
    # Fuses positional and acceleration values to determine subject speed
    # Acceleration comes from an IMU on the lower back
    # Position comes from BoS (Base of Support) summation over time

    # Functions:
    # __init__(): Contains Q and R arrays for modifying filter behaviour
    # reset(): Sets any changing variables to 0 for a new dataset to be processed
    # update(accelerometer, position, pitch, dt): Adds new values to filter and updates prediction
    # analyze_dataset(dataset): Iterates through data to post-process a complete dataset
    # smooth(input_arr, time_arr): Smooths curve

    # Usage:
    # Creating object:
    #   v_filter = kalman_filter_velocity()
    # Modifying Q and R coefficients:
    #   v_filter.Q_coeff = 0.0001
    # Using for Live Filtering (manual update):
    #   speed_current = v_filter.update([ac_x, ac_y, ac_z], pitch, position, sample_time)
    # Using for Post-Processing:
    #   speed_over_time = v_filter.analyze_dataset(dataset)
    #   Where dataset contains 6 sub-arrays for [time, ac_x, ac_y, ac_z, pitch, position]

    def __init__(self):
        self.reset()

        # Modifiable coefficient arrays
        self.Q_coeff = 0.0001
        self.Q = np.array([[1, 0],
                           [0, 1]]) * self.Q_coeff

        self.R_coeff = 0.001
        self.R = np.array([[1, 0],
                           [0, 10]]) * self.R_coeff

        # Variable Initializations
        self.C = np.array([[1, 0],
                           [0, 1]])


    def reset(self):
        self.ac_x = [0,0]
        self.ac_y = [0,0]
        self.ac_z = [0,0]

        self.x = np.transpose(np.array([[0, 0]]))

        self.P = np.array([[1, 0],
                           [0, 1]])

        # self.speed = 0

        self.current_position = 0


    def update(self, accelerometer, pitch, position, dt):
        self.ac_x.append(accelerometer[0])
        self.ac_y.append(accelerometer[0])
        self.ac_z.append(accelerometer[0])
        self.ac_x.pop(0)
        self.ac_y.pop(0)
        self.ac_z.pop(0)
        ac_x_mean = np.mean(self.ac_x)
        ac_y_mean = np.mean(self.ac_y)
        ac_z_mean = np.mean(self.ac_z)

        # Using pitch, approximate forward acceleration component
        ac_forward = ac_x_mean * np.cos(np.radians(pitch))
        #ac_forward = ac_y_mean * np.sin(np.radians(pitch))

        #self.speed = (1 - self.filter_c) * (self.speed + ac_forward_x * dt) + (self.filter_c * (position-self.current_position) / dt)
        speed_from_position = (position - self.current_position) / dt
        self.current_position = position

        # Calculate A and B arrays based on time step
        A = np.array([[1, dt],
                      [0, 1]])

        B = np.array([[-(dt**2)/2],
                      [dt]])

        # Assemble input matrices
        measured_input = np.transpose(np.array([[ac_forward]]))
        estimates = np.transpose(np.array([[speed_from_position]]))

        # Prediction equations
        x_new = (A.dot(self.x)) + (B.dot(measured_input))
        self.P = A.dot(self.P.dot(np.transpose(A))) + self.Q

        # Update equations
        y_new = estimates - self.C.dot(x_new)
        S = self.C.dot(self.P.dot(np.transpose(self.C))) + self.R
        K = self.P.dot(np.transpose(self.C).dot(np.linalg.inv(S)))
        x_new = x_new + K.dot(y_new)

        self.x = x_new
        self.P = (np.eye(2) - K.dot(self.C)).dot(self.P)

        return self.x[1][0]


    def analyze_dataset(self, dataset):
        # Dataset includes 6 subarrays
        time_arr = dataset[0]
        ac_x = dataset[1]
        ac_y = dataset[2]
        ac_z = dataset[3]
        pitch = dataset[4]
        position = dataset[5]

        self.reset()
        speed_arr = [0]
        for i in range(1, len(time_arr)):
            dt = time_arr[i] - time_arr[i-1]
            speed_arr.append(self.update([ac_x[i], ac_y[i], ac_z[i]], pitch[i], position[i], dt))
        return speed_arr


    def smooth(self, arr_to_smooth, time_arr, smooth_coeff=1):
        # Smooths input function using a univariate spline
        smoothed_arr = interpolate.UnivariateSpline(time_arr, arr_to_smooth, s=smooth_coeff)
        smoothed_arr = smoothed_arr(time_arr)
        return smoothed_arr