from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
import sys
from functools import partial
button_descriptions = [
    'Test1', 'Button2', 'PushMe3!'
]

class MyWidget(QWidget):
    def __init__(self, descriptions):
        super().__init__()
        layout = QGridLayout()
        self.dict_of_buttons = {}
        for i, description in enumerate(descriptions):
            self.dict_of_buttons[description] = QPushButton(description)
            self.dict_of_buttons[description].clicked.connect(partial(self.the_button_was_clicked, description))
            layout.addWidget(self.dict_of_buttons[description], i, 0)
        self.setLayout(layout)

    def the_button_was_clicked(self, key):
        self.dict_of_buttons[key].setText('{}: Enabled'.format(key))
        self.dict_of_buttons[key].setEnabled(False)

        for iter_key in self.dict_of_buttons:
            if iter_key != key:
                self.dict_of_buttons[iter_key].setText(iter_key)
                self.dict_of_buttons[iter_key].setEnabled(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        widget = MyWidget(button_descriptions)
        print(widget)
        # Set the central widget of the Window.
        self.setCentralWidget(widget)
        # Also change the window title.
        self.setWindowTitle("My Oneshot App")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
