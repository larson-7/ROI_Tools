if __name__ == '__main__':
    from step import Step
else:
    from .step import Step
from pypylon import pylon
import cv2

UNCONFIGURED = 0
CONFIGURED = 1
RAN_SUCCESS = 2
RAN_FAILED = 3

class AcquireImage(Step):
    type = "Image Acquisition"
    name = "Acquire Image"
    filepath_parameter = "image_filepath"

    def __init__(self, json=None):
        super().__init__(json)
        self.image = None


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

