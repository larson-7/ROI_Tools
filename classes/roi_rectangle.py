import numpy as np
from classes.point import Point
from classes.points import Points, init_args
from classes.rectangle import Rectangle
from classes.circle import Circle

def keep_within(method):
    def wrapper(*args):
        for arg in args
            if isinstance(arg, Point):
                if arg.x <=

        result = method(*args)

class ROIRectangle(Rectangle):
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

    @init_args
    def __init__(self, rectangle: Rectangle, image, windowName):
        # ROI geometry
        self.rectangle = rectangle
        self.tl_selection = None
        self.tm_selection = None
        self.tr_selection = None
        self.br_selection = None
        self.bm_selection = None
        self.bl_selection = None
        self.rotate = None
        self.box_size = 5

        # display & img properties
        # Image
        self.image = image
        self.image_display = self.image.copy()
        self.keepWithin = Rectangle([image.shape[0]/2, image.shape[1]/2], image.shape[0], image.shape[1])

        # Window name
        self.wname = windowName

        # calculate selection rectangles
        self.update()

    def update(self):
        self.tl_selection = Rectangle(self.rectangle.tl, self.box_size, self.box_size, self.rectangle.rotation)
        self.tm_selection = Rectangle((self.rectangle.tr - self.rectangle.tl)/2
                                      , self.box_size, self.box_size, self.rectangle.rotation)
        self.tr_selection = Rectangle(self.rectangle.tr, self.box_size, self.box_size, self.rectangle.rotation)
        self.br_selection = Rectangle(self.rectangle.br, self.box_size, self.box_size, self.rectangle.rotation)
        self.bm_selection = Rectangle((self.rectangle.bl - self.rectangle.br)/2
                                      , self.box_size, self.box_size, self.rectangle.rotation)
        self.bl_selection = Rectangle(self.rectangle.bl, self.box_size, self.box_size, self.rectangle.rotation)
        self.rotate = Circle(self.tm_selection.center + [0, 3/2 * self.box_size], self.box_size)

