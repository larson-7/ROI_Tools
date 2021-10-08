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

    return cam_list

class AcquireImage(Step):
    type = "Image Acquisition"
    name = "Acquire Image"
    filepath_parameter = "image_filepath"

    def __init__(self, json=None):
        super().__init__(json)
        self.image = None

    def display_inputs(self):
        self.combo = ComboBox(self)

        def populateCombo():
            cams = get_cam_list()
            if len(cams) != self.combo.count() or self.combo.count() < 1:
                self.combo.addItems(cams)




        combo.popupAboutToBeShown.connect(populateCombo)



        # combo box for list of available cameras
        self.camera_list_box = QComboBox()



        input_widget = QWidget()



        self.cb.addItems(["Java", "C#", "Python"])
        self.cb.currentIndexChanged.connect(self.selectionchange)

        layout.addWidget(self.cb)
        self.setLayout(layout)
        self.setWindowTitle("combo box demo")

    def selectionchange(self, i):
        print
        "Items in the list are :"

        for count in range(self.cb.count()):
            print
            self.cb.itemText(count)
        print
        "Current index", i, "selection changed ", self.cb.currentText()


        file_path.setWindowTitle("Image Filepath")
        file_path.selectionChanged.connect(self.is_valid)
        if self.filepath:
            file_path.setText(self.filepath)
        # grid layout settings
        # layout = QGridLayout()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('File Path'))
        layout.addWidget(file_path)
        input_widget.setLayout(layout)

        return input_widget

if __name__ == '__main__':

    '''
    A simple Program for grabing video from basler camera and converting it to opencv img.
    Tested on Basler acA1300-200uc (USB3, linux 64bit , python 3.5)
    '''


    # conecting to the first available camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

    # Grabing Continusely (video) with minimal delay
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    converter = pylon.ImageFormatConverter()

    # converting to opencv bgr format
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            # Access the image data
            image = converter.Convert(grabResult)
            img = image.GetArray()
            cv2.namedWindow('title', cv2.WINDOW_NORMAL)
            cv2.imshow('title', img)
            k = cv2.waitKey(1)
            if k == 27:
                break
        grabResult.Release()

    # Releasing the resource
    camera.StopGrabbing()

