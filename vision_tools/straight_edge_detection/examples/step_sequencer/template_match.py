from .step import Step

class TemplateMatch(Step):
    type = "Pattern Matching"
    filepath_parameter = "image_filepath"

    def __init__(self, json=None):
        super().__init__(json)
        self.image = None
