import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from step_sequencer.step_utilities import discover_steps

data = {"Image Acquisition": ["Load From File", "Acquire Image"],
        "Machine Vision Tools": ["Edge Find", "Pattern Match"],
        "Calculation": ["Expression", "Get Center"]}

data = discover_steps()
print(data)
class ProgramTreeItems(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(1)
        self.setHeaderLabels(["Available Steps"])
        items = []
        self.itemSelectionChanged.connect(self.get_current_index)

        for key, values in data.items():
            item = QTreeWidgetItem([key])

            for value in values:
                child = QTreeWidgetItem([str(value.__name__)])
                item.addChild(child)
            items.append(item)
            self.insertTopLevelItems(0, items)

    def get_current_index(self):
        getSelected = self.selectedItems()
        if getSelected.at(1):
            print(getSelected[0].text(0))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgramTreeItems()
    window.show()
    app.exec_()

