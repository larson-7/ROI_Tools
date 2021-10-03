from .step import Step

UNCONFIGURED = 0
CONFIGURED = 1
RAN_SUCCESS = 2
RAN_FAILED = 3

class FindLine(Step):
    type = "Edge Detection"
    name = "Find Line"

    def __init__(self, json=None):
        super().__init__(json)
