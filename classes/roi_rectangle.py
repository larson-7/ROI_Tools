import numpy as np
from classes.point import Point
from classes.points import Points, init_args
from classes.rectangle import Rectangle, RectAttributes
from classes.circle import Circle
import cv2


class ROIRectangle:
    def __init__(self, rectangle: Rectangle, image, window_name, box_size=8):
        # ROI geometry
        self.rectangle = rectangle
        self.tl_selection = None
        self.tm_selection = None
        self.tr_selection = None
        self.rm_selection = None
        self.br_selection = None
        self.bm_selection = None
        self.bl_selection = None
        self.lm_selection = None
        self.rotate_selection = None
        self.box_size = box_size
        self.geometries = []
        # calculate selection rectangles
        self.create_selections()
        # image variables
        self.wname = window_name
        self.image = image
        self.image_display = self.image.copy()
        # bounding rectangle of image window
        self.keep_within = Rectangle(RectAttributes((image.shape[0]/2, image.shape[1]/2), image.shape[0],
                                                    image.shape[1]))
        # Return flag
        self.return_flag = False

        # FLAGS
        # Rect already present
        self.active = False
        # Drag for rect resize in progress
        self.drag = False
        self.anchor = None

        # Marker flags by positions
        # Top left
        self.TL = False
        # Top middle
        self.TM = False
        # Top right
        self.TR = False
        # Left middle
        self.LM = False
        # Right middle
        self.RM = False
        # Bottom left
        self.BL = False
        # Bottom middle
        self.BM = False
        # Bottom right
        self.BR = False
        # Rotate flag
        self.Rotate = False
        # rectangle is being held down
        self.hold = False

    def create_selections(self):

        self.tl_selection = Rectangle(RectAttributes(self.rectangle.tl,
                                                     self.box_size, self.box_size, self.rectangle.rotation))

        self.tr_selection = Rectangle(RectAttributes(self.rectangle.tr,
                                                     self.box_size, self.box_size, self.rectangle.rotation))

        self.br_selection = Rectangle(RectAttributes(self.rectangle.br,
                                      self.box_size, self.box_size, self.rectangle.rotation))

        self.bl_selection = Rectangle(RectAttributes(self.rectangle.bl,
                                      self.box_size, self.box_size, self.rectangle.rotation))

        self.tm_selection = Rectangle(RectAttributes((self.rectangle.tr + self.rectangle.tl)/2,
                                      self.box_size, self.box_size, self.rectangle.rotation))

        self.rm_selection = Rectangle(RectAttributes((self.rectangle.tr + self.rectangle.br)/2,
                                      self.box_size, self.box_size, self.rectangle.rotation))

        self.bm_selection = Rectangle(RectAttributes((self.rectangle.bl + self.rectangle.br)/2,
                                      self.box_size, self.box_size, self.rectangle.rotation))

        self.lm_selection = Rectangle(RectAttributes((self.rectangle.tl + self.rectangle.bl)/2,
                                      self.box_size, self.box_size, self.rectangle.rotation))

        # generate a unit vector with correct direction and place rotate circle 2 box sizes normal of the TM selector
        diff = (self.rectangle.center - self.tm_selection.center)
        direction = diff/np.linalg.norm(diff)
        self.rotate_selection = Circle(self.tm_selection.center - direction * self.box_size * 2, self.box_size * 1.5)

        # populate list of all geometries
        self.geometries.append(self.rectangle)
        self.geometries.append(self.tl_selection)
        self.geometries.append(self.tm_selection)
        self.geometries.append(self.tr_selection)
        self.geometries.append(self.rm_selection)
        self.geometries.append(self.br_selection)
        self.geometries.append(self.bm_selection)
        self.geometries.append(self.bl_selection)
        self.geometries.append(self.lm_selection)
        self.geometries.append(self.rotate_selection)

    def update(self):

        self.tl_selection.attributes.center = self.rectangle.tl
        self.tl_selection.attributes.rotation = self.rectangle.rotation
        self.tl_selection.rect_from_attributes()


        self.tr_selection.attributes.center = self.rectangle.tr
        self.tr_selection.attributes.rotation = self.rectangle.rotation
        self.tr_selection.rect_from_attributes()

        self.br_selection.attributes.center = self.rectangle.br
        self.br_selection.attributes.rotation = self.rectangle.rotation
        self.br_selection.rect_from_attributes()

        self.bl_selection.attributes.center = self.rectangle.bl
        self.bl_selection.attributes.rotation = self.rectangle.rotation
        self.bl_selection.rect_from_attributes()

        self.tm_selection.attributes.center = (self.rectangle.tr + self.rectangle.tl)/2
        self.tm_selection.attributes.rotation = self.rectangle.rotation
        self.tm_selection.rect_from_attributes()

        self.rm_selection.attributes.center = (self.rectangle.tr + self.rectangle.br)/2
        self.rm_selection.attributes.rotation = self.rectangle.rotation
        self.rm_selection.rect_from_attributes()

        self.bm_selection.attributes.center = (self.rectangle.bl + self.rectangle.br)/2
        self.bm_selection.attributes.rotation = self.rectangle.rotation
        self.bm_selection.rect_from_attributes()

        self.lm_selection.attributes.center = (self.rectangle.tl + self.rectangle.bl)/2
        self.lm_selection.attributes.rotation = self.rectangle.rotation
        self.lm_selection.rect_from_attributes()

        # generate a unit vector with correct direction and place rotate circle 2 box sizes normal of the TM selector
        diff = (self.rectangle.center - self.tm_selection.center)
        direction = diff/np.linalg.norm(diff)
        self.rotate_selection.center = self.tm_selection.center - direction * self.box_size * 2

    def plot(self, image, color=(0, 255, 0), thickness=1):
        for contour in self.geometries:
            contour.plot(image, color, thickness)

    def dragrect(self, event, x, y, flags, param):
        mouse_pos = Point([x, y])
        # limit x & y to keep_within bounds of cv2 window
        if mouse_pos.x < self.keep_within.points[0][0]:
            mouse_pos.x = self.keep_within.points[0][0]
        if mouse_pos.y < self.keep_within.points[0][1]:
            mouse_pos.y = self.keep_within.points[0][1]
        if mouse_pos.x > self.keep_within.points[2][0] - 1:
            mouse_pos.x = self.keep_within.points[2][0] - 1
        if mouse_pos.y > self.keep_within.points[2][1] - 1:
            mouse_pos.y = self.keep_within.points[2][1] - 1
        # handle cv2 mouse events
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_down(mouse_pos)
        if event == cv2.EVENT_LBUTTONUP:
            self.mouse_up()
        if event == cv2.EVENT_MOUSEMOVE:
            self.mouse_move(mouse_pos)

    def mouse_down(self, mouse_pos):
        # determine if cursor is on any of the outer re-sizing 'buttons'
        if self.active:
            if Points.point_inside(self.tl_selection.points, mouse_pos):
                print('TM True')
                self.TL = True
                return

            if Points.point_inside(self.tm_selection.points, mouse_pos):
                print('TM True')
                self.TM = True
                return
            # print('Test')
            # print(mouse_pos)
            # print(self.tr_selection.points)
            if Points.point_inside(self.tr_selection.points, mouse_pos):
                print('TR TRUE')
                self.TR = True
                return
            # print('RM Lookup')
            # print('RM: ', self.rm_selection)
            # print('Mouse: ', mouse_pos)
            if Points.point_inside(self.rm_selection.points, mouse_pos):
                self.RM = True
                return
            
            if Points.point_inside(self.br_selection.points, mouse_pos):
                self.BR = True
                return

            if Points.point_inside(self.bm_selection.points, mouse_pos):
                self.BM = True
                return
                
            if Points.point_inside(self.bl_selection.points, mouse_pos):
                self.BL = True
                return

            if Points.point_inside(self.rm_selection.points, mouse_pos):
                self.RM = True
                return

            if Points.point_inside(self.lm_selection.points, mouse_pos):
                self.LM = True
                return

            if self.rotate_selection.point_inside(mouse_pos):
                self.Rotate = True
                return

            resize = np.any([self.TL, self.TR, self.BL, self.BR, self.TM, self.BM, self.LM, self.RM])
            if resize:
                pass

            # If event is inside rectangle and not in any button, translate whole rectangle
            # This has to be below all of the other conditions
            if Points.point_inside(self.rectangle.points, mouse_pos) and not resize:
                print('drag rectangle')
                self.hold = True
                self.anchor = mouse_pos
                return

        # Rectangle hasn't been created yet, set to active and record mouse position in outRect
        else:
            print('creating rectangle')
            self.anchor = mouse_pos
            print(self.rectangle.tl)
            self.drag = True
            self.active = True
            return

    def mouse_move(self, mouse_pos):
        # Rectangle is in process of being created, track where mouse is being dragged to
        if self.drag & self.active:
            delta = mouse_pos - self.anchor
            center = (mouse_pos + self.anchor) / 2

            if np.linalg.norm(delta) > 10:
                self.rectangle.attributes.width = delta.x
                self.rectangle.attributes.height = delta.y
                self.rectangle.attributes.center = center
                self.rectangle.rect_from_attributes()
                self.update()
                self.redraw()
                return

        elif self.hold:
            delta = mouse_pos - self.rectangle.center
            self.rectangle.points = Points.translate(self.rectangle.points, delta)
            self.rectangle.calc_attributes()
            self.update()
            self.redraw()
            return

        elif self.Rotate:
            rect_vector = self.tm_selection.center - self.rectangle.center
            mouse_vector = mouse_pos - self.rectangle.center
            angle = self.get_angle(rect_vector, mouse_vector)
            self.rectangle.points = Points.rotate(self.rectangle.points, angle, self.rectangle.center)
            self.rectangle.rotation += angle
            self.rectangle.calc_attributes()
            self.update()
            self.redraw()
            return

        elif self.RM:
            delta = mouse_pos - self.rm_selection.center

            # generate a unit vector with correct direction and multiply it by mouse delta
            diff = (self.rm_selection.center - self.rectangle.center)
            direction = diff / np.linalg.norm(diff)

            # NOTE This is element-wise multiplication not matrix
            directional_delta = delta * direction

            # rotated_x = delta.x * np.cos(self.rectangle.rotation) - \
            #                                   delta.y * np.sin(self.rectangle.rotation)
            # rotated_y = delta.x * np.sin(self.rectangle.rotation) + \
            #             delta.y * np.cos(self.rectangle.rotation)
            # print(rotated_y)
            if (mouse_pos.x - self.rectangle.br.x)*(self.rectangle.tr.y - self.rectangle.br.y) - \
                    (mouse_pos.y - self.rectangle.br.y)*(self.rectangle.tr.x - self.rectangle.br.x) > 0:
                delta_width = -np.linalg.norm(directional_delta)
                delta_center = delta_width * direction
            else:
                delta_width = np.linalg.norm(directional_delta)
                delta_center = delta_width * direction

            print(f'{delta=}')
            print(f'{diff=}')
            print(f'{direction=}')
            print(f'{directional_delta=}')

            self.rectangle.attributes.width += delta_width
            self.rectangle.attributes.center += 0.5 * delta_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            return


    # vector tools get angle of vector
    @staticmethod
    @init_args
    def get_angle(point1: Point, point2: Point):
        # Calculate unit vectors
        dot = point1[0] * point2[0] + point1[1] * point2[1]  # dot product between [x1, y1] and [x2, y2]
        det = point1[0] * point2[1] - point1[1] * point2[0]  # determinant
        angle = np.arctan2(det, dot)  # atan2(y, x) or atan2(sin, cos)
        return angle

    # Mouse was let up, drag turns off any active "button" selections
    def mouse_up(self):
        if self.active or (self.rectangle.attributes.width > 10 and self.rectangle.attributes.height > 10):
            self.drag = False
            self.TL = self.TM = self.TR = False
            self.LM = self.RM = False
            self.BL = self.BM = self.BR = False
            self.Rotate = False
            self.hold = False

    def redraw(self):
        self.image = self.image_display.copy()
        self.plot(self.image, color=(0, 0, 255))
