from .step import Step


class AcquireImage(Step):
    type = "Image Acquisition"
    filepath_parameter = "image_filepath"

    def __init__(self, json=None):
        super().__init__(json)
        self.image = None
