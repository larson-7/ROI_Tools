import cv2
import numpy as np
from classes.rectangle import Rectangle, RectAttributes


def inside_rect(rect, num_cols, num_rows):
    # Determine if the four corners of the rectangle are inside the rectangle with width and height
    # rect tuple
    # center (x,y), (width, height), angle of rotation (to the row)
    # center  The rectangle mass center.
    # center tuple (x, y): x is regarding to the width (number of columns) of the image, y is regarding to the height (number of rows) of the image.
    # size    Width and height of the rectangle.
    # angle   The rotation angle in a clockwise direction. When the angle is 0, 90, 180, 270 etc., the rectangle becomes an up-right rectangle.
    # Return:
    # True: if the rotated sub rectangle is side the up-right rectangle
    # False: else
    center = rect.attributes.center

    rect_center_x = center[0]
    rect_center_y = center[1]

    if (rect_center_x < 0) or (rect_center_x > num_cols):
        return False
    if (rect_center_y < 0) or (rect_center_y > num_rows):
        return False

    x_max = int(np.max(rect.points[:, 0]))
    x_min = int(np.min(rect.points[:, 0]))
    y_max = int(np.max(rect.points[:, 1]))
    y_min = int(np.min(rect.points[:, 1]))

    if (x_max <= num_cols) and (x_min >= 0) and (y_max <= num_rows) and (y_min >= 0):
        return True
    else:
        return False


def rect_bbx(rect):
    # Rectangle bounding box for rotated rectangle
    # Example:
    # rotated rectangle: height 4, width 4, center (10, 10), angle 45 degree
    # bounding box for this rotated rectangle, height 4*sqrt(2), width 4*sqrt(2), center (10, 10), angle 0 degree

    x_max = int(np.max(rect.points[:, 0]))
    x_min = int(np.min(rect.points[:, 0]))
    y_max = int(np.max(rect.points[:, 1]))
    y_min = int(np.min(rect.points[:, 1]))

    # Top-left
    # (x_min, y_min)
    # Top-right
    # (x_min, y_max)
    # Bottom-left
    #  (x_max, y_min)
    # Bottom-right
    # (x_max, y_max)
    # Width
    # y_max - y_min
    # Height
    # x_max - x_min
    # Center
    # (x_min + x_max) // 2, (y_min + y_max) // 2

    center = (int((x_min + x_max) // 2), int((y_min + y_max) // 2))
    width = int(x_max - x_min)
    height = int(y_max - y_min)
    angle = 0

    # return (center, (width, height), angle)
    return Rectangle(RectAttributes(center, width, height, angle))


def image_rotate_without_crop(mat, angle):
    # https://stackoverflow.com/questions/22041699/rotate-an-image-without-cropping-in-opencv-in-c
    # angle in degrees

    height, width = mat.shape[:2]
    image_center = (width / 2, height / 2)
    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1)
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    rotation_mat[0, 2] += bound_w / 2 - image_center[0]
    rotation_mat[1, 2] += bound_h / 2 - image_center[1]

    rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))

    return rotated_mat


def crop_rectangle(image, rect):
    # rect has to be upright

    num_rows = image.shape[0]
    num_cols = image.shape[1]

    if not inside_rect(rect=rect, num_cols=num_cols, num_rows=num_rows):
        print("Proposed rectangle is not fully in the image.")
        return None

    rect_center = rect.attributes.center
    rect_center_x = int(rect_center[0])
    rect_center_y = int(rect_center[1])
    rect_width = int(rect.attributes.width)
    rect_height = int(rect.attributes.height)

    return image[rect_center_y - rect_height // 2:rect_center_y + rect_height - rect_height // 2,
           rect_center_x - rect_width // 2:rect_center_x + rect_width - rect_width // 2]


def crop_rotated_rectangle(image, rect):
    # Crop a rotated rectangle from a image
    num_rows = image.shape[0]
    num_cols = image.shape[1]
    if not inside_rect(rect=rect, num_cols=num_cols, num_rows=num_rows):
        print("Proposed rectangle is not fully in the image.")
        return None

    rotated_angle = np.rad2deg(rect.attributes.rotation)

    rect_bbx_upright = rect_bbx(rect=rect)
    rect_bbx_upright_image = crop_rectangle(image=image, rect=rect_bbx_upright)
    rotated_rect_bbx_upright_image = image_rotate_without_crop(mat=rect_bbx_upright_image, angle=rotated_angle)

    rect_width = int(rect.attributes.width)
    rect_height = int(rect.attributes.height)
    crop_center = (rotated_rect_bbx_upright_image.shape[1] // 2, rotated_rect_bbx_upright_image.shape[0] // 2)

    return rotated_rect_bbx_upright_image[
           crop_center[1] - rect_height // 2: crop_center[1] + (rect_height - rect_height // 2),
           crop_center[0] - rect_width // 2: crop_center[0] + (rect_width - rect_width // 2)]
