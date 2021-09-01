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

    def dragrect(self, event, x, y, flags):
        x = int(x)
        y = int(y)
        # limit x & y to keepWithin bounds of cv2 window
        if x < self.keepWithin.points[0].x:
            x = self.keepWithin.points[0].x
        if y < self.keepWithin.points[0].y:
            y = self.keepWithin.points[0].y
        if x > self.keepWithin.points[2].x - 1:
            x = self.keepWithin.points[2].x - 1
        if y > self.keepWithin.points[2].y - 1:
            y = self.keepWithin.points[2].y - 1

        # handle cv2 mouse events
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouseDown(x, y)
        if event == cv2.EVENT_LBUTTONUP:
            self.mouseUp()
        if event == cv2.EVENT_MOUSEMOVE:
            self.mouseMove(x, y)

    def mouseDown(self, eX, eY):
        # determine if cursor is on any of the outer re-sizing 'buttons'
        if self.active:
            if pointInRect(eX, eY, Buttons.TL):
                dragObj.TL = True

            if pointInRect(eX, eY, Buttons.TR):
                dragObj.TR = True

            if pointInRect(eX, eY, Buttons.BL):
                dragObj.BL = True

            if pointInRect(eX, eY, Buttons.BR):
                dragObj.BR = True

            if pointInRect(eX, eY, Buttons.TM):
                dragObj.TM = True

            if pointInRect(eX, eY, Buttons.BM):
                dragObj.BM = True

            if pointInRect(eX, eY, Buttons.LM):
                dragObj.LM = True

            if pointInRect(eX, eY, Buttons.RM):
                dragObj.RM = True

            resize = np.any([dragObj.TL, dragObj.TR, dragObj.BL, dragObj.BR, dragObj.TM, dragObj.BM, dragObj.LM, dragObj.RM])
            if resize:
                dragObj.anchor = dragObj.outRect
                return

            # If event is inside rectangle and not in any button, translate whole rectangle
            # This has to be below all of the other conditions
            if pointInRect(eX, eY, dragObj.outRect) and not resize:
                print('drag rectangle')
                dragObj.anchor.center.x = eX - dragObj.outRect.center.x
                dragObj.anchor.w = dragObj.outRect.w
                dragObj.anchor.center.y = eY - dragObj.outRect.center.y
                dragObj.anchor.h = dragObj.outRect.h
                dragObj.hold = True
                return

        # Rectangle hasn't been created yet, set to active and record mouse position in outRect
        else:
            print('start creation of rectangle')
            #TODO: FIX
            dragObj.anchor.points[2].x = eX - dragObj.outRect.points[2].x
            dragObj.anchor.points[2].y = eY - dragObj.outRect.points[2].y

            dragObj.outRect.points[0].x = eX
            dragObj.outRect.points[0].y = eY
            dragObj.drag = True
            dragObj.active = True
            return