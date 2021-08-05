# Imports
import cv2
import math
import numpy as np


class Point:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __repr__(self):
         return '({0},{1})'.format(self.x, self.y)
    def __add__(self, v):
        return Point(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        return Point(self.x - v.x, self.y - v.y)

    def __mul__(self, s):
        return Point(self.x * s, self.y * s)


class Rect:
    def __init__(self, x, y, w, h, angle):
        # Center Point
        self.center = Point(x, y)
        # Height and Width
        self.w = w
        self.h = h
        self.angle = angle
        self.box_size = 4

        # Rectangle Vertices
        self.points = [Point(0, 0), Point(0, 0), Point(0, 0), Point(0, 0)]
        self.top_middle = Point(0, 0)
        self.right_middle = Point(0, 0)
        self.bot_middle = Point(0, 0)
        self.left_middle = Point(0, 0)
        self.rotate_pos = Point(0, 0)
        self.get_vertices_points()

    def get_dims(self):
        hypot = math.sqrt((self.points[0].x - self.points[2].x)**2 + (self.points[0].y - self.points[2].y)**2)
        angle = math.radians(45)
        self.w = math.cos(angle) * hypot
        self.h = math.sin(angle) * hypot

    def get_vertices_points(self):
        width, height, angle = self.w, self.h, self.angle
        cos = math.cos(angle)
        sin = math.sin(angle)

        # Top Left (TL):
        self.points[0].x = int(self.center.x - width / 2 * cos - height / 2 * sin)
        self.points[0].y = int(self.center.y - width / 2 * sin - height / 2 * cos)
        # Top Right (TR):
        self.points[1].x = int(self.center.x + width / 2 * cos + height / 2 * sin)
        self.points[1].y = int(self.center.y + width / 2 * sin - height / 2 * cos)
        # Bottom Right (BR):
        self.points[2].x = int(self.center.x + width / 2 * cos + height / 2 * sin)
        self.points[2].y = int(self.center.y + width / 2 * sin + height / 2 * cos)
        # Bottom Left (BL):
        self.points[3].x = int(self.center.x - width / 2 * cos - height / 2 * sin)
        self.points[3].y = int(self.center.y + width / 2 * sin + height / 2 * cos)


        # Store separately from rectangle vertices, because they are not essential to rectangle's geometry
        # Top Middle (TM):
        self.top_middle.x = int(self.center.x * cos - (self.center.y - height / 2) * sin)
        self.top_middle.y = int(self.center.x * sin + (self.center.y - height / 2) * cos)

        # Right Middle (RM):
        self.right_middle.x = int((self.center.x + width / 2) * cos - self.center.y * sin)
        self.right_middle.y = int((self.center.x + width / 2) * sin + self.center.y * cos)

        # Bottom Middle (BM):
        self.bot_middle.x = int(self.center.x * cos - (self.center.y + height / 2) * sin)
        self.bot_middle.y = int(self.center.x * sin + (self.center.y + height / 2) * cos)

        # Left Middle (LM):
        self.left_middle.x = int((self.center.x - width / 2) * cos - self.center.y * sin)
        self.left_middle.y = int((self.center.x - width / 2) * sin + self.center.y * cos)

        # Rotate Position (Rotate):
        self.rotate_pos.x = int(self.top_middle.x - 1/8 * height * sin)
        self.rotate_pos.y = int(self.top_middle.y - 1/8 * height * cos)


class RoiButton:
    def __init__(self, rect_obj, box_size=8):
        # define all button rectangles
        self.TL = Rect(rect_obj.points[0].x, rect_obj.points[0].y, box_size, box_size, 0)
        self.TR = Rect(rect_obj.points[1].x, rect_obj.points[1].y, box_size, box_size, 0)
        self.BR = Rect(rect_obj.points[2].x, rect_obj.points[2].y, box_size, box_size, 0)
        self.BL = Rect(rect_obj.points[3].x, rect_obj.points[3].y, box_size, box_size, 0)

        self.TM = Rect(rect_obj.top_middle.x, rect_obj.top_middle.y, box_size, box_size, 0)
        self.RM = Rect(rect_obj.right_middle.x, rect_obj.right_middle.y, box_size, box_size, 0)
        self.BM = Rect(rect_obj.bot_middle.x, rect_obj.bot_middle.y, box_size, box_size, 0)
        self.LM = Rect(rect_obj.left_middle.x, rect_obj.left_middle.y, box_size, box_size, 0)
        self.Rotate = Rect(rect_obj.rotate_pos.x, rect_obj.rotate_pos.y, box_size, box_size, 0)


class DragRectangle:
    # Limits on the canvas
    keepWithin = Rect(0, 0, 0, 0, 0)
    # To store rectangle
    outRect = Rect(0, 0, 0, 0, 0)
    # To store rectangle anchor point
    # Here the rect class object is used to store
    # the distance in the x and y direction from
    # the anchor point to the top-left and the bottom-right corner
    anchor = Rect(0, 0, 0, 0, 0)
    # Selection marker size
    sBlk = 4
    # Rotation angle of rectangle
    theta = 0

    # Whether initialized or not
    initialized = False

    # Image
    image = None
    image_display = None

    # Window Name
    wname = ""

    # Return flag
    returnflag = False

    # FLAGS
    # Rect already present
    active = False
    # Drag for rect resize in progress
    drag = False

    # Marker flags by positions
    # Top left
    TL = False
    # Top middle
    TM = False
    # Top right
    TR = False
    # Left middle
    LM = False
    # Right middle
    RM = False
    # Bottom left
    BL = False
    # Bottom middle
    BM = False
    # Bottom right
    BR = False
    # Rotate flag
    Rotate = False
    # rectangle is being held down
    hold = False

    def __init__(self, Img, windowName, windowWidth, windowHeight):
        # Image
        self.image = Img
        self.image_display = self.image.copy()

        # Window name
        self.wname = windowName

        # Limit the selection box to the canvas
        self.keepWithin.center.x = windowWidth/2
        self.keepWithin.center.y = windowHeight/2
        self.keepWithin.w = windowWidth
        self.keepWithin.h = windowHeight
        self.keepWithin.get_vertices_points()

        # Set rect to zero width and height
        self.outRect.center.x = 0
        self.outRect.center.y = 0
        self.outRect.w = 0
        self.outRect.h = 0

def dragrect(event, x, y, flags, dragObj):
    x = int(x)
    y = int(y)
    # limit x & y to keepWithin bounds of cv2 window
    if x < dragObj.keepWithin.points[0].x:
        x = dragObj.keepWithin.points[0].x
    if y < dragObj.keepWithin.points[0].y:
        y = dragObj.keepWithin.points[0].y
    if x > dragObj.keepWithin.points[2].x - 1:
        x = dragObj.keepWithin.points[2].x - 1
    if y > dragObj.keepWithin.points[2].y - 1:
        y = dragObj.keepWithin.points[2].y - 1

    # handle cv2 mouse events
    if event == cv2.EVENT_LBUTTONDOWN:
        mouseDown(x, y, dragObj)
    if event == cv2.EVENT_LBUTTONUP:
        mouseUp(dragObj)
    if event == cv2.EVENT_MOUSEMOVE:
         mouseMove(x, y, dragObj)
    if event == cv2.EVENT_LBUTTONDBLCLK:
        mouseDoubleClick(x, y, dragObj)


def pointInRect(pX, pY, dragObj):
    x1 = dragObj.points[0].x
    y1 = dragObj.points[0].y
    x2 = dragObj.points[2].x
    y2 = dragObj.points[2].y

    if (x1 < pX and pX < x2):
        if (y1 < pY and pY < y2):
            return True
    return False


# TODO determine why double click isnt working
def mouseDoubleClick(eX, eY, dragObj):
    print('in double click')
    if dragObj.active:
        if pointInRect(eX, eY, dragObj.outRect.x, dragObj.outRect.y, dragObj.outRect.w, dragObj.outRect.h):
            dragObj.returnflag = True
            cv2.destroyWindow(dragObj.wname)


def mouseDown(eX, eY, dragObj):
    # determine if cursor is on any of the outer re-sizing 'buttons'
    print('mouse down')
    if dragObj.active:
        Buttons = RoiButton(dragObj.outRect)

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


def mouseMove(eX, eY, dragObj):
    # Rectangle is in process of being created, track where mouse is being dragged to
    if dragObj.drag & dragObj.active:
        dragObj.outRect.points[2].x = eX - dragObj.anchor.points[2].x
        dragObj.outRect.points[2].y = eY - dragObj.anchor.points[2].y

        dragObj.outRect.center = midpoint(dragObj.outRect.points[0], dragObj.outRect.points[2])
        dragObj.outRect.get_dims()
        dragObj.outRect.get_vertices_points()
        clearCanvasNDraw(dragObj)
        return

    if dragObj.hold:
        # update new x and y positions with mouse position and original anchor point
        dragObj.outRect.center.x = eX - dragObj.anchor.center.x
        dragObj.outRect.center.y = eY - dragObj.anchor.center.y
        dragObj.outRect.get_vertices_points()

    if dragObj.TL:
        print('dragging rectangle, TL')
    if dragObj.TM:
        print('dragging rectangle, TM')
    if dragObj.TR:
        print('dragging rectangle, TR')
    if dragObj.RM:
        print('dragging rectangle, RM')
    if dragObj.BR:
        print('dragging rectangle, BR')
    if dragObj.BM:
        print('dragging rectangle, BM')
    if dragObj.BL:
        print('dragging rectangle, BL')
    if dragObj.RM:
        print('dragging rectangle, RM')

    # TODO: These need to be in rotation coords and account for both x and y regardless of direction ... ugh
    # Top-left was selected: need to adjust center position(x,y), width, and height
    if dragObj.TL:
        delta_x = dragObj.outRect.points[0].x - eX
        delta_y = dragObj.outRect.points[0].y - eY

        dragObj.outRect.points[0].x += delta_x
        dragObj.outRect.points[0].y += delta_y
        dragObj.outRect.center = midpoint(dragObj.outRect.points[0], dragObj.outRect.points[2])
        dragObj.outRect.w += delta_x
        dragObj.outRect.h += delta_y

        dragObj.outRect.get_vertices_points()

    # Bottom-right was selected: need to adjust width and height
    if dragObj.BR:
        delta_x = dragObj.outRect.points[2].x - eX
        delta_y = dragObj.outRect.points[2].y - eY

        dragObj.outRect.points[2].x = eX
        dragObj.outRect.points[2].y = eY
        dragObj.outRect.center = midpoint(dragObj.outRect.points[2], dragObj.outRect.points[0])
        dragObj.outRect.w += delta_x
        dragObj.outRect.h += delta_y

        dragObj.outRect.get_vertices_points()

    # Top-Right was selected: need to adjust start position(y), width, and height
    if dragObj.TR:
        delta_x = dragObj.outRect.points[1].x - eX
        delta_y = dragObj.outRect.points[1].y - eY

        dragObj.outRect.points[1].x = eX
        dragObj.outRect.points[1].y = eY
        dragObj.outRect.center = midpoint(dragObj.outRect.points[1], dragObj.outRect.points[3])
        dragObj.outRect.w += delta_x
        dragObj.outRect.h += delta_y

        dragObj.outRect.get_vertices_points()

    # Bottom-Left was selected: need to adjust start position(x), width, and height
    if dragObj.BL:
        delta_x = dragObj.outRect.points[3].x - eX
        delta_y = dragObj.outRect.points[3].y - eY

        dragObj.outRect.points[3].x = eX
        dragObj.outRect.points[3].y = eY
        dragObj.outRect.center = midpoint(dragObj.outRect.points[3], dragObj.outRect.points[1])
        dragObj.outRect.w += delta_x
        dragObj.outRect.h += delta_y

        dragObj.outRect.get_vertices_points()
    # TODO: FIX THIS LOL
    # Top-Middle was selected: need to adjust start position(y) and height
    if dragObj.TM:
        delta_y = dragObj.outRect.top_middle.y - eY
        print(f'{delta_y=}')
        dragObj.outRect.top_middle.y = eY
        line_segment = dragObj.outRect.bot_middle - dragObj.outRect.top_middle
        dragObj.outRect.center = midpoint(dragObj.outRect.top_middle, dragObj.outRect.bot_middle)
        dragObj.outRect.h += delta_y
        print(f'{line_segment=}')
        dragObj.outRect.get_vertices_points()

    # Bottom-Middle was selected: need to adjust height
    if dragObj.BM:
        delta_y = eY - dragObj.outRect.bot_middle.y
        dragObj.outRect.bot_middle.y = eY

        dragObj.outRect.center = midpoint(dragObj.outRect.bot_middle, dragObj.outRect.top_middle)
        dragObj.outRect.h += delta_y
        dragObj.outRect.get_vertices_points()

    # Left-Middle was selected: need to adjust start position(x) and width
    if dragObj.LM:
        delta_x = dragObj.outRect.left_middle.x - eX

        dragObj.outRect.left_middle.x = eX
        dragObj.outRect.center = midpoint(dragObj.outRect.left_middle, dragObj.outRect.right_middle)
        dragObj.outRect.w += delta_x
        dragObj.outRect.get_vertices_points()

    # Right-Middle was selected: need to adjust width
    if dragObj.RM:
        delta_x = dragObj.outRect.right_middle.x - eX
        dragObj.outRect.right_middle.x = eX

        dragObj.outRect.center = midpoint(dragObj.outRect.right_middle, dragObj.outRect.left_middle)
        dragObj.outRect.w += delta_x
        dragObj.outRect.get_vertices_points()

    # limit x & y to keepWithin bounds of cv2 window
    if dragObj.outRect.points[0].x < dragObj.keepWithin.points[0].x + 1:
        dragObj.outRect.center.x = dragObj.outRect.center.x + \
                                   (dragObj.keepWithin.points[0].x - dragObj.outRect.points[0].x + 1)
        dragObj.outRect.get_vertices_points()

    if dragObj.outRect.points[0].y < dragObj.keepWithin.points[0].y + 1:
        dragObj.outRect.center.y = dragObj.outRect.center.y + \
                                   (dragObj.keepWithin.points[0].y - dragObj.outRect.points[0].y + 1)
        dragObj.outRect.get_vertices_points()

    if dragObj.outRect.points[2].x > dragObj.keepWithin.points[2].x - 1:
        dragObj.outRect.center.x = dragObj.outRect.center.x + \
                                   (dragObj.keepWithin.points[2].x - dragObj.outRect.points[2].x - 1)
        dragObj.outRect.get_vertices_points()

    if dragObj.outRect.points[2].y > dragObj.keepWithin.points[2].y - 1:
        dragObj.outRect.center.y = dragObj.outRect.center.y + \
                                   (dragObj.keepWithin.points[2].y - dragObj.outRect.points[2].y - 1)
        dragObj.outRect.get_vertices_points()

    clearCanvasNDraw(dragObj)
    straightenUpRect(dragObj)
    return

# Mouse was let up, drag turns off any active "button" selections
def mouseUp(dragObj):
    dragObj.drag = False
    disableResizeButtons(dragObj)
    # TODO: watch out for this function, over 180deg of rotation could mess up
    # TODO: if theta > 0, drag tools need to scale perpendicular to rectangle and incorporate angle
    straightenUpRect(dragObj)
    if dragObj.outRect.w == 0 or dragObj.outRect.h == 0:
        dragObj.active = False

    clearCanvasNDraw(dragObj)


def disableResizeButtons(dragObj):
    dragObj.TL = dragObj.TM = dragObj.TR = False
    dragObj.LM = dragObj.RM = False
    dragObj.BL = dragObj.BM = dragObj.BR = False
    dragObj.hold = False


def midpoint(p1, p2):
    return Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)


def straightenUpRect(dragObj):
    """
    Make sure x, y, w, h of the Rect are positive
    """
    if dragObj.outRect.w < 0:
        dragObj.outRect.center.x = dragObj.outRect.center.x + dragObj.outRect.w
        dragObj.outRect.w = -dragObj.outRect.w
    if dragObj.outRect.h < 0:
        dragObj.outRect.center.y = dragObj.outRect.center.y + dragObj.outRect.h
        dragObj.outRect.h = -dragObj.outRect.h


def clearCanvasNDraw(dragObj):
    # Draw
    dragObj.image = dragObj.image_display.copy()
    rect = ((dragObj.outRect.center.x, dragObj.outRect.center.y), (dragObj.outRect.w, dragObj.outRect.h), dragObj.outRect.angle)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(dragObj.image, [box], 0, (0, 255, 0), 2)
    drawSelectMarkers(dragObj.image, dragObj)

def drawSelectMarkers(image, dragObj):
    """
    Draw markers on the dragged rectangle
    """
    Buttons = RoiButton(dragObj.outRect)
    # Top-Left
    cv2.rectangle(image, (Buttons.TL.points[0].x, Buttons.TL.points[0].y),
                  (Buttons.TL.points[2].x, Buttons.TL.points[2].y), (0, 255, 0), 2)
    # Top-Right
    cv2.rectangle(image, (Buttons.TR.points[0].x, Buttons.TR.points[0].y),
                  (Buttons.TR.points[2].x, Buttons.TR.points[2].y), (0, 255, 0), 2)
    # Bottom-Left
    cv2.rectangle(image, (Buttons.BL.points[0].x, Buttons.BL.points[0].y),
                  (Buttons.BL.points[2].x, Buttons.BL.points[2].y), (0, 255, 0), 2)
    # Bottom-Right
    cv2.rectangle(image, (Buttons.BR.points[0].x, Buttons.BR.points[0].y),
                  (Buttons.BR.points[2].x, Buttons.BR.points[2].y), (0, 255, 0), 2)
    # Top-Mid
    cv2.rectangle(image, (Buttons.TM.points[0].x, Buttons.TM.points[0].y),
                  (Buttons.TM.points[2].x, Buttons.TM.points[2].y), (0, 255, 0), 2)
    # Bottom-Mid
    cv2.rectangle(image, (Buttons.BM.points[0].x, Buttons.BM.points[0].y),
                  (Buttons.BM.points[2].x, Buttons.BM.points[2].y), (0, 255, 0), 2)
    # Left-Mid
    cv2.rectangle(image, (Buttons.LM.points[0].x, Buttons.LM.points[0].y),
                  (Buttons.LM.points[2].x, Buttons.LM.points[2].y), (0, 255, 0), 2)
    # Right-Mid
    cv2.rectangle(image, (Buttons.RM.points[0].x, Buttons.RM.points[0].y),
                  (Buttons.RM.points[2].x, Buttons.RM.points[2].y), (0, 255, 0), 2)
    # Rotate
    cv2.rectangle(image, (Buttons.Rotate.points[0].x, Buttons.Rotate.points[0].y),
                  (Buttons.Rotate.points[2].x, Buttons.Rotate.points[2].y), (0, 255, 0), 2)
