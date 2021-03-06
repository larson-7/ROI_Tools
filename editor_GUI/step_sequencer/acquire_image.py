if __name__ == '__main__':
    from step import Step
else:
    from .step import Step

from pypylon import pylon
from pypylon import genicam
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QTextEdit, QFileDialog, QVBoxLayout, QComboBox,\
    QFormLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore
import cv2
import os
import sys
import time

os.environ["PYLON_CAMEMU"] = "3"
# The bandwidth used by a FireWire camera device can be limited by adjusting the packet size.
maxCamerasToUse = 1

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
    return cam_list, cameras

class AcquireImage(Step):
    type = "Image Acquisition"
    name = "Acquire Image"
    filepath_parameter = "image_filepath"

    def __init__(self, json=None):
        super().__init__(json)
        self.cam_index = 0
        self.cams, self.cam_refs = get_cam_list()

    def selection_change(self, i):
        self.cam_index = i


    def execute(self, commands=None, counter=None):
        start_time = time.time()
        camera = self.cam_refs[self.cam_index]

        # Register the standard configuration event handler for enabling software triggering.
        # The software trigger configuration handler replaces the default configuration
        # as all currently registered configuration handlers are removed by setting the registration mode to RegistrationMode_ReplaceAll.
        camera.RegisterConfiguration(pylon.SoftwareTriggerConfiguration(), pylon.RegistrationMode_ReplaceAll,
                                     pylon.Cleanup_Delete)
        camera.Open()

        # This strategy can be useful when the acquired images are only displayed on the screen.
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)


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
            self.__class__.images[self.output_image_index] = image.GetArray()
            self.__class__.display_image = self.__class__.images[self.output_image_index]
            end_time = time.time()
            print('acqusition time', end_time - start_time)
            self.status = RAN_SUCCESS

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

    def index_changed(self, index):
        self.output_image_index = index

    def display_outputs(self):
        output_widget = QWidget()
        combo = QComboBox()
        # populate list of available images
        for i, image in enumerate(self.images):
            combo.addItem('Image: {}'.format(i))
        # connect combo box methods
        combo.currentIndexChanged.connect(self.index_changed)
        combo.setCurrentIndex(self.output_image_index)
        # layout settings
        layout = QFormLayout()
        layout.addRow(QLabel('Output Image'), combo)
        # layout.addWidget(combo)
        output_widget.setLayout(layout)
        return output_widget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    step = AcquireImage()
    window = step.display_inputs()
    window.show()
    app.exec_()

