from __future__ import annotations

import sys

from qtpy.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from utility.gui.qt.widgets.widgets.combobox import (
    ButtonDelegate,
    CustomListView,
    FilterComboBox,
    FilterProxyModel,
    filter_line_edit_key_press_event as filterLineEditKeyPressEvent,
)

__all__ = [
    "FilterComboBox",
    "FilterProxyModel",
    "ButtonDelegate",
    "filterLineEditKeyPressEvent",
    "CustomListView",
]


if __name__ == "__main__":

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("FilterComboBox Test")
            self.setGeometry(100, 100, 300, 200)
            central_widget: QWidget = QWidget(self)
            self.setCentralWidget(central_widget)
            layout: QVBoxLayout = QVBoxLayout(central_widget)
            self.combo_box: FilterComboBox = FilterComboBox()
            self.combo_box.populate_combo_box(
                [f"Item {i}" for i in range(10)],
            )
            layout.addWidget(self.combo_box)
            central_widget.setLayout(layout)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
