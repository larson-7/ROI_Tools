if __name__ == '__main__':
    from step import Step
else:
    from .step import Step

from pypylon import pylon
from pypylon import genicam
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QTextEdit, QFileDialog, QVBoxLayout, QComboBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore
import cv2
import os
import sys
import time

os.environ["PYLON_CAMEMU"] = "3"

# Number of images to be grabbed.
countOfImagesToGrab = 10

# Limits the amount of cameras used for grabbing.
# It is important to manage the available bandwidth when grabbing with multiple cameras.
# This applies, for instance, if two GigE cameras are connected to the same network adapter via a switch.
# To manage the bandwidth, the GevSCPD interpacket delay parameter and the GevSCFTD transmission delay
# parameter can be set for each GigE camera device.
# The "Controlling Packet Transmission Timing with the Interpacket and Frame Transmission Delays on Basler GigE Vision Cameras"
# Application Notes (AW000649xx000)
# provide more information about this topic.
# The bandwidth used by a FireWire camera device can be limited by adjusting the packet size.
maxCamerasToUse = 2

# The exit code of the sample application.
exitCode = 0

#Step enumerated statues
UNCONFIGURED = 0
CONFIGURED = 1
RAN_SUCCESS = 2
RAN_FAILED = 3

class ComboBox(QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()

def get_cam_list():
    cam_list = []
    # Get the transport layer factory.
    tlFactory = pylon.TlFactory.GetInstance()
    # Get all attached devices and exit application if no device is found.
    devices = tlFactory.EnumerateDevices()
    if len(devices) == 0:
        raise pylon.RuntimeException("No camera present.")

    # Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
    cameras = pylon.InstantCameraArray(min(len(devices), maxCamerasToUse))

    # Create and attach all Pylon Devices.
    for i, cam in enumerate(cameras):
        cam.Attach(tlFactory.CreateDevice(devices[i]))
        # Print the model name of the camera.
        cam_list.append(cam.GetDeviceInfo().GetModelName())
    return cam_list, cam

class AcquireImage(Step):
    type = "Image Acquisition"
    name = "Acquire Image"
    filepath_parameter = "image_filepath"

    def __init__(self, json=None):
        super().__init__(json)
        self.image = None
        self.cam_index = 0
        self.cams, self.cam_refs = get_cam_list()

    def selection_change(self, i):
        self.cam_index = i


    def execute(self, commands=None, counter=None):
        start_time = time.time()
        camera = self.cam_refs[self.cam_index]
        print('here')
        print(camera)
        # Execute the software trigger, wait actively until the camera accepts the next frame trigger or until the timeout occurs.
        if camera.WaitForFrameTriggerReady(200, pylon.TimeoutHandling_ThrowException):
            camera.ExecuteSoftwareTrigger()

        # Only the last received image is waiting in the internal output queue
        # and is now retrieved.
        # The grabbing continues in the background, e.g. when using hardware trigger mode.

        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_Return)

        # Stop the grabbing.
        camera.StopGrabbing()

        if grabResult.GrabSucceeded():
            # converting to opencv bgr format
            converter = pylon.ImageFormatConverter()
            converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            # Access the image data
            image = converter.Convert(grabResult)
            self.image = image.GetArray()
            end_time = time.time()
            print(end_time - start_time)

        grabResult.Release()


    def display_inputs(self):

        input_widget = QWidget()
        combo = ComboBox()

        # populate list of available cameras
        if len(self.cams) != combo.count() or combo.count() < 1:
            combo.addItems(self.cams)
        # update cam_resource value
        combo.currentIndexChanged.connect(self.selection_change)
        # input layout
        layout = QVBoxLayout()
        layout.addWidget(combo)
        input_widget.setLayout(layout)

        return input_widget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    step = AcquireImage()
    window = step.display_inputs()
    window.show()
    app.exec_()

