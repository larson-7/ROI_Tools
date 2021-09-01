import numpy as np
from classes.point import Point
from classes.points import Points, init_args
from classes.rectangle import Rectangle, RectAttributes
from classes.circle import Circle
import cv2


class ROIRectangle:
    def __init__(self, rectangle: Rectangle, image, window_name, box_size=5):
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
        self.update()
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

    def update(self):
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
        self.rotate_selection = Circle(self.tm_selection.center - direction * self.box_size * 2, self.box_size)
        print(self.rotate_selection)

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
                self.TL = True

            if Points.point_inside(self.tm_selection.points, mouse_pos):
                self.TM = True

            if Points.point_inside(self.tr_selection.points, mouse_pos):
                self.TR = True

            if Points.point_inside(self.rm_selection.points, mouse_pos):
                self.RM = True
            
            if Points.point_inside(self.br_selection.points, mouse_pos):
                self.BR = True

            if Points.point_inside(self.bm_selection.points, mouse_pos):
                self.BM = True
                
            if Points.point_inside(self.bl_selection.points, mouse_pos):
                self.BL = True

            if Points.point_inside(self.rm_selection.points, mouse_pos):
                self.RM = True
                
            if Points.point_inside(self.rotate_selection.points, mouse_pos):
                self.Rotate = True

            resize = np.any([self.TL, self.TR, self.BL, self.BR, self.TM, self.BM, self.LM, self.RM])
            if resize:
                pass

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

            if delta != [0, 0]:
                self.rectangle.attributes.width = delta.x
                self.rectangle.attributes.height = delta.y
                self.rectangle.attributes.center = center
                self.rectangle.rect_from_attributes()
                # print(self.rectangle)
                self.update()
                self.redraw()

    # Mouse was let up, drag turns off any active "button" selections
    def mouse_up(self):
        self.drag = False

    def redraw(self):
        self.image = self.image_display.copy()
        self.plot(self.image, color=(0, 0, 255))
