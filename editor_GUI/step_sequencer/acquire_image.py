from .step import Step

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
