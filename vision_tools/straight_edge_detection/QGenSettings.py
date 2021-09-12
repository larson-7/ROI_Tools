from gen_settings_ui import Ui_gen_settings
from PyQt5 import QtWidgets


class Gen_Settings(QtWidgets.QWidget, Ui_gen_settings):
    def __init__(self, parent=None):
        super(Gen_Settings, self).__init__(parent)
        self.setupUi(self)