import numpy as np
from classes.point import Point
from classes.points import Points, init_args
from classes.rectangle import Rectangle, RectAttributes
from classes.circle import Circle
import cv2


class ROIRectangle:
    def __init__(self, rectangle: Rectangle, image, window_name, box_size=8, thickness=3):
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
        self.selection_delta = np.array([0, 0])
        self.box_size = box_size
        self.line_thickness = int(thickness)
        self.prev_mouse_pos = np.array([0, 0])
        self.geometries = []
        # calculate selection rectangles
        self.create_selections()
        # image variables
        self.wname = window_name
        self.image = image
        self.image_display = self.image.copy()
        self.img_center = (image.shape[1]/2, image.shape[0]/2)
        # bounding rectangle of image window
        self.keep_within = Rectangle(RectAttributes(self.img_center, image.shape[1],
                                                    image.shape[0]))
        # Return flag
        self.return_flag = False

        # FLAGS
        # Rect already present
        self.active = False
        # Drag for rect resize in progress
        self.drag = False
        self.anchor = None
        self.updateimg = True

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

    def plot(self, image, color=(0, 255, 0), thickness=5):
        for contour in self.geometries:
            contour.plot(image, color, thickness)
        # plot arrow on rectangle to determine normal search direction
        arrow_start = (int(self.tl_selection.attributes.center[0]), int(self.tl_selection.attributes.center[1]))
        arrow_end = self.tl_selection.attributes.center + (self.tm_selection.attributes.center -
                                                           self.tl_selection.attributes.center)/2
        cv2.arrowedLine(image, arrow_start,
                        (int(arrow_end[0]), int(arrow_end[1])),
                        (0, 0, 255), 3, tipLength=0.2)

    def dragrect(self, event, x, y, flags, param):
        mouse_pos = Point([x, y])
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
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.mouse_dclick(mouse_pos)

    def mouse_down(self, mouse_pos):

        self.prev_mouse_pos = mouse_pos
        # determine if cursor is on any of the outer re-sizing 'buttons'
        if self.active:
            if Points.point_inside(self.tl_selection.points, mouse_pos):
                self.TL = True
                self.selection_delta = mouse_pos - self.tl_selection.center
            if Points.point_inside(self.tm_selection.points, mouse_pos):
                self.TM = True
                self.selection_delta = self.tm_selection.center - mouse_pos
            if Points.point_inside(self.tr_selection.points, mouse_pos):
                self.TR = True
                self.selection_delta = self.tr_selection.center - mouse_pos
            if Points.point_inside(self.rm_selection.points, mouse_pos):
                self.RM = True
                self.selection_delta = self.rm_selection.center - mouse_pos
            if Points.point_inside(self.br_selection.points, mouse_pos):
                self.BR = True
                self.selection_delta = self.br_selection.center - mouse_pos
            if Points.point_inside(self.bm_selection.points, mouse_pos):
                self.BM = True
                self.selection_delta = self.bm_selection.center - mouse_pos
            if Points.point_inside(self.bl_selection.points, mouse_pos):
                self.BL = True
                self.selection_delta = self.bl_selection.center - mouse_pos
            if Points.point_inside(self.rm_selection.points, mouse_pos):
                self.RM = True
                self.selection_delta = self.rm_selection.center - mouse_pos
            if Points.point_inside(self.lm_selection.points, mouse_pos):
                self.LM = True
                self.selection_delta = self.lm_selection.center - mouse_pos
            if self.rotate_selection.point_inside(mouse_pos):
                self.Rotate = True

            resize = np.any([self.TL, self.TR, self.BL, self.BR, self.TM, self.BM, self.LM, self.RM])
            if resize:
                self.anchor = mouse_pos
                return

            # If event is inside rectangle and not in any button, translate whole rectangle
            # This has to be below all of the other conditions
            if Points.point_inside(self.rectangle.points, mouse_pos):
                self.hold = True
                self.anchor = mouse_pos
                return

        # Rectangle hasn't been created yet, set to active and record mouse position in outRect
        else:
            self.anchor = mouse_pos
            self.drag = True
            self.active = True
            return

    def mouse_move(self, mouse_pos):
        mouse_delta = mouse_pos - self.prev_mouse_pos
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

            self.rectangle.points = Points.translate(self.rectangle.points, mouse_delta)
            self.rectangle.calc_attributes()
            self.update()
            self.redraw()
            self.prev_mouse_pos = mouse_pos
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
            # generate a unit vector with correct direction and multiply it by mouse delta
            diff = (self.rm_selection.center - self.rectangle.center)
            direction = diff / np.linalg.norm(diff)

            # NOTE This is element-wise multiplication not matrix
            directional_delta = mouse_delta * direction

            # check which direction of the selector the mouse is on, need to do this because of 360 rotation
            if (mouse_pos.x - self.rectangle.br.x)*(self.rectangle.tr.y - self.rectangle.br.y) - \
                    (mouse_pos.y - self.rectangle.br.y)*(self.rectangle.tr.x - self.rectangle.br.x) > 0:
                delta_width = -np.linalg.norm(directional_delta)
                delta_center = delta_width * direction
            else:
                delta_width = np.linalg.norm(directional_delta)
                delta_center = delta_width * direction

            self.rectangle.attributes.width += delta_width
            self.rectangle.attributes.center += 0.5 * delta_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            self.prev_mouse_pos = mouse_pos
            return

        elif self.LM:
            # generate a unit vector with correct direction and multiply it by mouse delta
            diff = (self.lm_selection.center - self.rectangle.center)
            direction = diff / np.linalg.norm(diff)

            # NOTE This is element-wise multiplication not matrix
            directional_delta = mouse_delta * direction
            # check which direction of the selector the mouse is on, need to do this because of 360 rotation
            if (mouse_pos.x - self.rectangle.tl.x)*(self.rectangle.bl.y - self.rectangle.tl.y) - \
                    (mouse_pos.y - self.rectangle.tl.y)*(self.rectangle.bl.x - self.rectangle.tl.x) > 0:
                delta_width = -np.linalg.norm(directional_delta)
                delta_center = delta_width * direction
            else:
                delta_width = np.linalg.norm(directional_delta)
                delta_center = delta_width * direction

            self.rectangle.attributes.width += delta_width
            self.rectangle.attributes.center += 0.5 * delta_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            self.prev_mouse_pos = mouse_pos
            return

        elif self.TM:
            # generate a unit vector with correct direction and multiply it by mouse delta
            diff = (self.tm_selection.center - self.rectangle.center)
            direction = diff / np.linalg.norm(diff)

            # NOTE This is element-wise multiplication not matrix
            directional_delta = mouse_delta * direction

            # check which direction of the selector the mouse is on, need to do this because of 360 rotation
            if (mouse_pos.x - self.rectangle.tr.x)*(self.rectangle.tl.y - self.rectangle.tr.y) - \
                    (mouse_pos.y - self.rectangle.tr.y)*(self.rectangle.tl.x - self.rectangle.tr.x) > 0:
                delta_height = -np.linalg.norm(directional_delta)
                delta_center = delta_height * direction
            else:
                delta_height = np.linalg.norm(directional_delta)
                delta_center = delta_height * direction

            self.rectangle.attributes.height += delta_height
            self.rectangle.attributes.center += 0.5 * delta_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            self.prev_mouse_pos = mouse_pos
            return

        elif self.BM:
            # generate a unit vector with correct direction and multiply it by mouse delta
            diff = (self.bm_selection.center - self.rectangle.center)
            direction = diff / np.linalg.norm(diff)

            # NOTE This is element-wise multiplication not matrix
            directional_delta = mouse_delta * direction

            # check which direction of the selector the mouse is on, need to do this because of 360 rotation
            if (mouse_pos.x - self.rectangle.bl.x)*(self.rectangle.br.y - self.rectangle.bl.y) - \
                    (mouse_pos.y - self.rectangle.bl.y)*(self.rectangle.br.x - self.rectangle.bl.x) > 0:
                delta_height = -np.linalg.norm(directional_delta)
                delta_center = delta_height * direction
            else:
                delta_height = np.linalg.norm(directional_delta)
                delta_center = delta_height * direction

            self.rectangle.attributes.height += delta_height
            self.rectangle.attributes.center += 0.5 * delta_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            self.prev_mouse_pos = mouse_pos
            return

        elif self.TR:

            # generate a unit vector with correct direction and multiply it by mouse delta
            diff = (self.tr_selection.center - self.rectangle.center)
            direction = diff / np.linalg.norm(diff)

            # NOTE This is element-wise multiplication not matrix
            directional_delta = mouse_delta * direction
            magnitude_vector = np.linalg.norm(directional_delta)
            sin = np.sin(self.rectangle.rotation)
            cos = np.cos(self.rectangle.rotation)

            # check which direction of the selector the mouse is on, need to do this because of 360 rotation
            if (mouse_pos.x - self.tr_selection.br.x)*(self.tr_selection.tl.y - self.tr_selection.br.y) - \
                    (mouse_pos.y - self.tr_selection.br.y)*(self.tr_selection.tl.x - self.tr_selection.br.x) > 0:
                # shrink rectangle
                delta_width = -magnitude_vector
                delta_height = -magnitude_vector
                x_comp = -magnitude_vector * cos - (magnitude_vector * sin)
                y_comp = -magnitude_vector * sin + (magnitude_vector * cos)

            else:
                # expand rectangle
                delta_width = magnitude_vector
                delta_height = magnitude_vector
                x_comp = magnitude_vector * cos - (-magnitude_vector * sin)
                y_comp = magnitude_vector * sin + (-magnitude_vector * cos)
            delta_center = 0.5 * np.array([x_comp, y_comp])

            self.rectangle.attributes.height += delta_height
            self.rectangle.attributes.width += delta_width
            self.rectangle.attributes.center += delta_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            self.prev_mouse_pos = mouse_pos
            return

        elif self.TL:
            # generate a unit vector with correct direction and multiply it by mouse delta
            diff = (self.tl_selection.center - self.rectangle.center)
            direction = diff / np.linalg.norm(diff)

            # NOTE This is element-wise multiplication not matrix
            directional_delta = mouse_delta * direction
            magnitude_vector = np.linalg.norm(directional_delta)
            sin = np.sin(self.rectangle.rotation)
            cos = np.cos(self.rectangle.rotation)

            # check which direction of the selector the mouse is on, need to do this because of 360 rotation
            if (mouse_pos.x - self.tl_selection.tr.x)*(self.tl_selection.bl.y - self.tl_selection.tr.y) - \
                    (mouse_pos.y - self.tl_selection.tr.y)*(self.tl_selection.bl.x - self.tl_selection.tr.x) > 0:
                # shrink rectangle
                delta_width = -magnitude_vector
                delta_height = -magnitude_vector
                x_comp = magnitude_vector * cos - (magnitude_vector * sin)
                y_comp = magnitude_vector * sin + (magnitude_vector * cos)

            else:
                # expand rectangle
                delta_width = magnitude_vector
                delta_height = magnitude_vector
                x_comp = -magnitude_vector * cos - (-magnitude_vector * sin)
                y_comp = -magnitude_vector * sin + (-magnitude_vector * cos)
            delta_center = 0.5 * np.array([x_comp, y_comp])

            self.rectangle.attributes.height += delta_height
            self.rectangle.attributes.width += delta_width
            self.rectangle.attributes.center += delta_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            self.prev_mouse_pos = mouse_pos
            return

        elif self.BL:
            # generate a unit vector with correct direction and multiply it by mouse delta
            diff = (self.bl_selection.center - self.rectangle.center)
            direction = diff / np.linalg.norm(diff)

            # NOTE This is element-wise multiplication not matrix
            directional_delta = mouse_delta * direction
            magnitude_vector = np.linalg.norm(directional_delta)
            sin = np.sin(self.rectangle.rotation)
            cos = np.cos(self.rectangle.rotation)

            # check which direction of the selector the mouse is on, need to do this because of 360 rotation
            if (mouse_pos.x - self.bl_selection.tl.x) * (self.bl_selection.br.y - self.bl_selection.tl.y) - \
                    (mouse_pos.y - self.bl_selection.tl.y) * (self.bl_selection.br.x - self.bl_selection.tl.x) > 0:
                # shrink rectangle
                delta_width = -magnitude_vector
                delta_height = -magnitude_vector
                x_comp = magnitude_vector * cos - (-magnitude_vector * sin)
                y_comp = magnitude_vector * sin + (-magnitude_vector * cos)

            else:
                # expand rectangle
                delta_width = magnitude_vector
                delta_height = magnitude_vector
                x_comp = -magnitude_vector * cos - (magnitude_vector * sin)
                y_comp = -magnitude_vector * sin + (magnitude_vector * cos)
            delta_center = 0.5 * np.array([x_comp, y_comp])

            self.rectangle.attributes.height += delta_height
            self.rectangle.attributes.width += delta_width
            self.rectangle.attributes.center += delta_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            self.prev_mouse_pos = mouse_pos
            return

        elif self.BR:
            # generate a unit vector with correct direction and multiply it by mouse delta
            diff = (self.br_selection.center - self.rectangle.center)
            direction = diff / np.linalg.norm(diff)

            # NOTE This is element-wise multiplication not matrix
            directional_delta = mouse_delta * direction
            magnitude_vector = np.linalg.norm(directional_delta)
            sin = np.sin(self.rectangle.rotation)
            cos = np.cos(self.rectangle.rotation)

            # check which direction of the selector the mouse is on, need to do this because of 360 rotation
            if (mouse_pos.x - self.br_selection.bl.x) * (self.br_selection.tr.y - self.br_selection.bl.y) - \
                    (mouse_pos.y - self.br_selection.bl.y) * (self.br_selection.tr.x - self.br_selection.bl.x) > 0:
                # shrink rectangle
                delta_width = -magnitude_vector
                delta_height = -magnitude_vector
                x_comp = -magnitude_vector * cos - (-magnitude_vector * sin)
                y_comp = -magnitude_vector * sin + (-magnitude_vector * cos)

            else:
                # expand rectangle
                delta_width = magnitude_vector
                delta_height = magnitude_vector
                x_comp = magnitude_vector * cos - (magnitude_vector * sin)
                y_comp = magnitude_vector * sin + (magnitude_vector * cos)
            delta_center = 0.5 * np.array([x_comp, y_comp])

            self.rectangle.attributes.height += delta_height
            self.rectangle.attributes.width += delta_width
            self.rectangle.attributes.center += delta_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            self.prev_mouse_pos = mouse_pos
            return

    def mouse_dclick(self, mouse_pos):
        if self.rotate_selection.point_inside(mouse_pos):
            self.rectangle.rotation = 0
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()
            return
        if Points.point_inside(self.rectangle.points, mouse_pos):

            self.rectangle.center = self.img_center
            self.rectangle.rect_from_attributes()
            self.update()
            self.redraw()

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
        self.plot(self.image, color=(0, 0, 255), thickness=self.line_thickness)
        self.updateimg = True
