import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from PyQt5 import QtCore
from step_sequencer.step_utilities import discover_steps

data = {"Image Acquisition": ["Load From File", "Acquire Image"],
        "Machine Vision Tools": ["Edge Find", "Pattern Match"],
        "Calculation": ["Expression", "Get Center"]}

data = discover_steps()
print(data)


class ProgramTreeItems(QTreeWidget):
    def __init__(self, step):
        super().__init__()
        self.count = 0
        self.setColumnCount(1)
        self.setHeaderLabels(["Available Steps"])
        items = []
        self.itemSelectionChanged.connect(self.get_current_index)
        self.step = step
        self.doubleClicked.connect(self.on_doubleClicked)
        for key, values in data.items():
            item = QTreeWidgetItem([key])

            for value in values:
                child = QTreeWidgetItem([str(value.__name__)])
                item.addChild(child)
            items.append(item)
            self.insertTopLevelItems(0, items)


    def get_current_index(self):
        getSelected = self.selectedItems()
        if getSelected[0].parent():
            print(getSelected[0].text(0))

    @QtCore.pyqtSlot("QModelIndex")
    def on_doubleClicked(self, ix):
        print(self.count)
        self.count += 1
        print('ix data: ', ix.data())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgramTreeItems()
    window.show()
    app.exec_()

