from .step import Step


class FindLine(Step):
    type = "Edge Detection"

    def __init__(self, json=None):
        super().__init__(json)
