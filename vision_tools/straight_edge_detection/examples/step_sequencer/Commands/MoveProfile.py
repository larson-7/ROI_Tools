import sqlite3
import numpy as np
import random
from Command import Command, auto
import sys
import math

class MoveProfile(Command):

    type = "move_profile"

    def __init__(self, json):
        super().__init__(json)

        # Init constants
        self.random = True
        self.database = "/Users/Jordan/PycharmProjects/Object_Detection/SQL/mouse_movements.sqlite"
        self.table = "Mouse"
        self.start_index = 0
        self.end_index = 0
        self.db = None
        self.num_entries = 0
        self.mouse_offset = (7, 15)

        try:
            self.result = json["result"]
            self.get_result = True
            self.valid_result = False
        except KeyError:
            try:
                self.x = json["x"]
                self.y = json["y"]
                self.get_result = False

            except KeyError:
                print("Backend: Error: either 'x' or 'y' is not found in:\n ", json)
                sys.exit(1)
        try:
            self.fuzzy = json["fuzzy"]
        except KeyError:
            self.fuzzy = False

    def __enter__(self):
        # Connect to database
        self.db = sqlite3.connect(self.database)

        # Get number of database entries
        self.num_entries = self.get_num_entries()

        # if random is selected, grab a random index to start, else use 0
        if self.random:
            self.start_index = random.randint(0, self.num_entries)
        else:
            self.start_index = 0


    def __exit__(self, exc_type, exc_val, exc_tb):
        # close database connection
        self.db.close()

    def check_connect(self):
        if not self.db:
            self.__enter__()

    def execute(self, commands, commands_counter):

        # Any duration less than this is rounded to 0.0 to instantly move the mouse.
        auto.MINIMUM_DURATION = 0  # Default: 0.1
        # Minimal number of seconds to sleep between mouse moves.

        auto.MINIMUM_SLEEP = 0  # Default: 0.05
        # The number of seconds to pause after EVERY public function call.
        auto.PAUSE = 0  # Default: 0.1


        if self.get_result:
            for command in commands:
                # print('command names: {}'.format(command.name))
                command_to_find = self.result.split(".")
                if command.name == command_to_find[0]:
                    self.x, self.y = getattr(command, command_to_find[1])
                    self.valid_result = True
                    break

            if not self.valid_result:
                print("Backend: Error: invalid result name and/or attribute:\n ", self.result)
                sys.exit(1)

        if self.fuzzy:
            desired_x = self.x - self.mouse_offset[0] + random.uniform(-1,1)
            desired_y = self.y - self.mouse_offset[1] + random.uniform(-1,1)
        else:
            desired_x = self.x - self.mouse_offset[0]
            desired_y = self.y - self.mouse_offset[1]

        # print('move to desired location: {}'.format((self.x, self.y)))
        current_position = np.array(auto.position())

        current_pos_off = np.array(current_position + self.mouse_offset)

        desired_vector = np.array([current_pos_off, (desired_x, desired_y )])
        print('({0}) pos: {1}, move to: {2}'.format(self.name, desired_vector[0], desired_vector[1]))

        # bug in profiles, check if end point is equal to desired end point
        retry_count = 0
        while retry_count < 5:
            # get mouse profile
            mouse_profile, times = self.get_profile(desired_vector)
            error = np.linalg.norm(mouse_profile[len(mouse_profile) - 1] - desired_vector[1])
            if error < 3:
                break
            else:
                print("({0}): endpoint not correct, retrying...".format(self.name))
                print("desired: {}, profile end: {}".format(desired_vector[1], mouse_profile[len(mouse_profile) - 1]))
                retry_count += 1


        # get delta times between points
        dts = times[1:] - times[:-1]

        # scale velocities by random value
        # dts = dts * random.uniform(0.2, 0.5)

        # Iterate through points
        for point, dt in zip(mouse_profile, dts):

            auto.moveTo(*point)
            speed = 900
            x_now, y_now = auto.position()
            length = math.sqrt(pow(abs(point[0] - x_now), 2) + pow(abs(point[1] - y_now), 2))
            if length < 500:
                speed *= 0.6
            elif length < 400:
                speed *= 0.5
            elif length < 300:
                speed *= 0.4
            elif length < 200:
                speed *= 0.3
            elif length < 100:
                speed *= 0.2

            speed = 100 if speed < 100 else speed  # limit minimum speed
            time = length / speed
            auto.sleep(time)

        # move cursor offset so cursor tip is centered
        auto.move(self.mouse_offset[0], self.mouse_offset[1])
        auto.sleep(random.uniform(0.01, 0.2))

    # TODO: error handling to check valid input coords
    def is_valid(self):
        return True

    def is_valid(self):
        if self.get_result:
            return isinstance(self.result, str)
        else:
            return isinstance(self.x, (int, float)) and isinstance(self.y, (int, float))


    # ###############################
    # static supporting class methods
    # ###############################

    def get_num_entries(self):
        # check if db object is initialized
        self.check_connect()
        sql = '''SELECT
        COUNT(*)
        FROM
        {};'''.format(self.table)

        # Execute Query and fetch result
        cursor = self.db.execute(sql)
        query_result = cursor.fetchone()
        return query_result[0]


    def get_mouse_profile(self):

        failed_count = 0

        while True:

            # check if db object is initialized
            self.check_connect()

            # calc dynamics of mouse profile
            # velocity_profile, accel_profile = self.get_motion(profile, time)

            # check number of entries
            self.num_entries = self.get_num_entries()
            # print('start index {}'.format(self.start_index))
            # if random is selected, get a new random start index
            if self.random:
                self.start_index = random.randint(0, self.num_entries - 100)
            # else go to next index and wrap back to 0 if at end
            else:
                if self.end_index + 10 >= self.num_entries:
                    self.start_index = 0
                else:
                    self.start_index = self.end_index + 1

            # Format start query to find first 0 entry for button
            sql = '''SELECT rowid
               FROM Mouse
               WHERE rowid > {} AND button = 0
               ORDER BY timestamp
               LIMIT 1
               '''.format(self.start_index)

            # Execute Query and fetch result
            cursor = self.db.execute(sql)
            query_result = cursor.fetchone()
            self.start_index = query_result[0]
            print('move_start_index: {}'.format(self.start_index))


            # Format Query to find next entry with button = 1
            sql = '''SELECT rowid
               FROM Mouse
               WHERE rowid > {} AND button = 1
               ORDER BY timestamp
               LIMIT 1
               '''.format(self.start_index)

            # Execute Query and fetch result
            cursor = self.db.execute(sql)
            query_result = cursor.fetchone()
            self.end_index = query_result[0]

            # Format Query grab subset of entries beginning with start_index
            # and ending with end_index
            sql = '''SELECT x,y
               FROM Mouse
               WHERE rowid >= {} AND rowid <= {}
               ORDER BY timestamp
               '''.format(self.start_index, self.end_index)

            # Execute Query and fetch result
            cursor = self.db.execute(sql)
            profile = np.array(cursor.fetchall())

            ''' Grab Mouse Timestamp Data '''
            # Format Query grab subset of entries beginning with start_index
            # and ending with end_index
            sql = '''SELECT timestamp
                            FROM Mouse
                            WHERE rowid >= {} AND rowid <= {}
                            ORDER BY timestamp
                            '''.format(self.start_index, self.end_index)

            # Execute Query and fetch result
            cursor = self.db.execute(sql)
            timestamp = np.array(cursor.fetchall(), dtype=np.datetime64)
            # convert array to (n,) from (n,1) need to understand why it assigned it like that in the first place
            timestamp = timestamp.reshape(timestamp.shape[0])
            time = (timestamp[1:] - timestamp[0])
            time = time * 1 / np.timedelta64(1, 's')
            time = np.insert(time, 0, 0.0)

            if profile.size > 10 or failed_count > 15:
                break
            else:
                print('profile too short, retrying')
                failed_count += 1

        #   return an array of points that is a mouse profile
        # print('end index{}'.format(self.end_index))
        return profile, time


    # vector tools get magnitude of vector
    @staticmethod
    def get_magnitude(array):
        # Get start and end points for mouse profile
        vector = array[len(array) - 1] - array[0]
        # Return magnitude
        return np.linalg.norm(vector)


    # vector tools get angle of vector
    @staticmethod
    def get_angle(array, array_2):
        # Get start and end points from array
        vector = array[len(array) - 1] - array[0]

        # Get start and end points from array
        vector_2 = array_2[len(array_2) - 1] - array_2[0]

        # Calculate unit vectors
        dot = vector[0] * vector_2[0] + vector[1] * vector_2[1]  # dot product between [x1, y1] and [x2, y2]
        det = vector[0] * vector_2[1] - vector[1] * vector_2[0]  # determinant
        angle = np.arctan2(det, dot)  # atan2(y, x) or atan2(sin, cos)

        return angle


    # vector tools translate any n x 2 series of vectors
    @staticmethod
    def translate(array, t):
        if array.shape[1] < 3:
            # Create a new row of 1s the length of the number of rows in array
            ones = np.ones(array.shape[0])

            # Create a 3 x n matrix
            matrix = np.c_[array, ones]
        else:
            matrix = array
        # Translation matrix, A
        A = np.array([[1, 0, t[0]],
                      [0, 1, t[1]],
                      [0, 0, 1]])
        # Compute translation operation
        result = A @ matrix.T
        result = result.T
        return result[0:result.shape[0], 0:2]


    # vector tools rotate any n x 2 series of vectors
    @staticmethod
    def rotate(array, angle):
        matrix = array
        # Rotation matrix, A
        A = np.array([[np.cos(angle), -np.sin(angle)],
                      [np.sin(angle), np.cos(angle)]])

        # Compute translation operation
        result = A @ matrix.T
        result = result.T
        return result[0:result.shape[0], 0:2]


    # vector tools scale any n x 2 series of vectors
    @staticmethod
    def scale(array, s):
        if array.shape[1] < 3:
            # Create a new row of 1s the length of the number of cols in array
            # ones = np.ones(array.shape[0])
            # Create a 2 x n matrix
            # matrix = np.c_[array, ones]
            matrix = array
        else:
            matrix = array
        # Scaling matrix, A
        A = np.array([[s, 0],
                      [0, s]])
        # Compute translation operation
        result = A @ matrix.T
        result = result.T
        return result[0:result.shape[0], 0:2]


    @staticmethod
    def get_motion(position_array, time_array):
        # get xy magnitude
        diff = position_array[1:] - position_array[:-1]
        magnitude = np.hypot(diff[:, 0], diff[:, 1])
        # get dt time change in seconds
        dt = (time_array[1:] - time_array[:-1])
        # velocity in pix/sec
        velocity = np.divide(magnitude, dt)
        # accel in pix/sec^2
        acceleration = np.divide((velocity[1:] - velocity[:-1]), (time_array[2:] - time_array[1:-1]))
        # acceleration = np.append(0, acceleration)
        return velocity, acceleration


    def get_profile(self, desired_vector):

        # get mouse profile
        mouse_profile, times = self.get_mouse_profile()
        # Translate both the mouse profile and desired vector to the origin (0,0)
        desired_vector_t = self.translate(desired_vector, -desired_vector[0, 0:2])
        mouse_profile_t = self.translate(mouse_profile, -mouse_profile[0, 0:2])

        """ Scaling of profile """
        # get magnitude of both data sets
        desired_mag = self.get_magnitude(desired_vector_t)
        profile_mag = self.get_magnitude(mouse_profile_t)

        # calculate scale
        scale = desired_mag / profile_mag

        # scale velocity by vector scale ratio
        times = times * scale

        # Scale mouse profile
        scaled_mouse_profile = self.scale(mouse_profile_t, scale)

        # Get first and last points of scaled profile
        scaled_mouse_vector = np.array((scaled_mouse_profile[0, 0:2],
                                        scaled_mouse_profile[scaled_mouse_profile.shape[0] - 1, 0:2]))

        """ Rotation of profile """
        # Get vector angle
        vector_angle = self.get_angle(scaled_mouse_vector, desired_vector_t)

        # Rotate mouse profile
        rotate_mouse_profile = self.rotate(scaled_mouse_profile, vector_angle)

        ''' Translate the mouse profile vector back to desired vector start '''
        offset = desired_vector[0, 0:2] - rotate_mouse_profile[0, 0:2]

        # Translate to desired start position, final mouse profile
        final_mouse_profile = self.translate(rotate_mouse_profile, offset)
        return final_mouse_profile, times


