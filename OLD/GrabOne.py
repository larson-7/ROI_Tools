from pypylon import pylon
from pypylon import genicam
import numpy
import time
import cv2

startTime = time.time()
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

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
buffersInQueue = 0

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
    img = image.GetArray()
    end_time = time.time()
    print(end_time - startTime)

grabResult.Release()

