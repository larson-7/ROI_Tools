import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from PyQt5 import QtCore


data = {"Image Acquisition": ["Load From File", "Acquire Image"],
        "Machine Vision Tools": ["Edge Find", "Pattern Match"],
        "Calculation": ["Expression", "Get Center"]}


class ProgramTreeItems(QTreeWidget):
    def __init__(self, qlist, available_steps):
        super().__init__()
        self.setColumnCount(1)
        self.setHeaderLabels(["Available Steps"])
        items = []
        self.itemSelectionChanged.connect(self.get_current_index)
        self.qlist = qlist
        self.doubleClicked.connect(self.on_doubleClicked)
        self.selectedProgram = None
        self.available_steps = available_steps
        for key, values in self.available_steps.items():
            item = QTreeWidgetItem([key])

            for value in values:
                child = QTreeWidgetItem([str(value.__name__)])
                item.addChild(child)
            items.append(item)
            self.insertTopLevelItems(0, items)

    def get_current_index(self):
        getSelected = self.selectedItems()
        if getSelected[0].parent():
            self.qlist.selected_program = getSelected[0].text(0)
        else:
            self.qlist.selected_program = None

    @QtCore.pyqtSlot("QModelIndex")
    def on_doubleClicked(self, ix):
        if ix.parent().data():
            self.qlist.selected_program = ix.data()
            # add double-clicked item to program list
            self.qlist.add()
        else:
            self.qlist.selected_program = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgramTreeItems()
    window.show()
    app.exec_()

