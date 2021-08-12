import numpy as np
import matplotlib.pyplot as plt

# Python Imaging Library imports
from PIL import Image
from PIL import ImageDraw


def get_rect(x, y, width, height, angle):
    rect = np.array([(0, 0), (width, 0), (width, height), (0, height), (0, 0)])
    theta = (np.pi / 180.0) * angle
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])
    offset = np.array([x, y])
    transformed_rect = np.dot(rect, R) + offset
    return transformed_rect


def get_data():
    """Make an array for the demonstration."""
    X, Y = np.meshgrid(np.linspace(0, np.pi, 512), np.linspace(0, 2, 512))
    z = (np.sin(X) + np.cos(Y)) ** 2 + 0.25
    data = (255 * (z / z.max())).astype(int)
    return data


if __name__ == "__main__":
    data = get_data()

    # Convert the numpy array to an Image object.
    img = Image.fromarray(data)

    # Draw a rotated rectangle on the image.
    draw = ImageDraw.Draw(img)
    rect = get_rect(x=120, y=80, width=100, height=40, angle=30.0)
    draw.polygon([tuple(p) for p in rect], fill=0)
    # Convert the Image data to a numpy array.
    new_data = np.asarray(img)

    # Display the result using matplotlib.  (`img.show()` could also be used.)
    plt.imshow(new_data, cmap=plt.cm.gray)
    plt.show()