import csv
import sys
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui


class SpinBoxDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, QStyleOptionViewItem, QModelIndex):
        editor = QtWidgets.QSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(0)
        editor.setMaximum(10_000)
        editor.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        return editor

    def setEditorData(self, QWidget, QModelIndex):
        value = int(QModelIndex.model().data(QModelIndex, QtCore.Qt.EditRole))

        QWidget.setValue(value)

    def setModelData(self, QWidget, QAbstractItemModel, QModelIndex):
        QWidget.interpretText()
        value = QWidget.value()
        QAbstractItemModel.setData(QModelIndex, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, QWidget, QStyleOptionViewItem, QModelIndex):
        QWidget.setGeometry(QStyleOptionViewItem.rect)


class DoubleSpinBoxDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, QStyleOptionViewItem, QModelIndex):
        editor = QtWidgets.QDoubleSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(0)
        editor.setMaximum(1_000_000)
        editor.setDecimals(2)
        editor.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        return editor

    def setEditorData(self, QWidget, QModelIndex):
        value = float(QModelIndex.model().data(QModelIndex, QtCore.Qt.EditRole))
        QWidget.setValue(value)

    def setModelData(self, QWidget, QAbstractItemModel, QModelIndex):
        value = QWidget.text()
        QAbstractItemModel.setData(QModelIndex, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, QWidget, QStyleOptionViewItem, QModelIndex):
        QWidget.setGeometry(QStyleOptionViewItem.rect)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.centralwidget = QtWidgets.QWidget(self)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.MainTable = QtWidgets.QTableWidget(self.centralwidget)
        self.spinbox_delegate = SpinBoxDelegate()
        self.double_spinbox_delegate = DoubleSpinBoxDelegate()
        self.setup_ui()
        self.last_menu_pos = QtCore.QPoint(0, 0)

    def setup_ui(self):

        self.resize(500, 250)
        # set context menus to custom
        self.MainTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        # build table
        self.MainTable.setGridStyle(QtCore.Qt.NoPen)
        self.MainTable.setColumnCount(4)
        self.MainTable.verticalHeader().setVisible(False)
        self.MainTable.setItemDelegateForColumn(1, self.double_spinbox_delegate)
        self.MainTable.setItemDelegateForColumn(2, self.double_spinbox_delegate)
        self.MainTable.setItemDelegateForColumn(3, self.spinbox_delegate)
        for i in range(4):
            item = QtWidgets.QTableWidgetItem()
            self.MainTable.setHorizontalHeaderItem(i, item)

        self.MainTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.MainTable.setAlternatingRowColors(True)

        header = self.MainTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        header.setHighlightSections(False)

        self.gridLayout.addWidget(self.MainTable, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.localize()
        self.connect_actions()
        self.MainTable.customContextMenuRequested.connect(self.build_table_context, QtCore.Qt.UniqueConnection)
        self.MainTable.itemChanged.connect(self.changed, QtCore.Qt.UniqueConnection)
        self.customContextMenuRequested.connect(self.build_main_context, QtCore.Qt.UniqueConnection)

    def changed(self, item):
        if item.column() == 0:
            self.MainTable.resizeColumnToContents(0)
        if item.column() == 3:
            self.update_jumps()

    def update_jumps(self):
        # sum all values in 3rd column
        total_jumps = sum(
            int(self.MainTable.item(i, 3).text()) for i in
            range(self.MainTable.rowCount()))

        if total_jumps:
            self.MainTable.horizontalHeaderItem(3).setText(f"Jumps {total_jumps}")
        else:
            self.MainTable.horizontalHeaderItem(3).setText("Jumps")
        self.MainTable.resizeColumnToContents(3)

    def connect_actions(self):
        self.delete_row_action = QtWidgets.QAction("Delete row")
        self.add_row_action = QtWidgets.QAction("Add row")
        self.load_file_action = QtWidgets.QAction("Load file")
        self.clear_table_action = QtWidgets.QAction("Clear table contents")
        self.save_file_action = QtWidgets.QAction("Save file")
        self.delete_row_action.triggered.connect(self.delete_row)
        self.add_row_action.triggered.connect(self.add_row)
        self.load_file_action.triggered.connect(self.load_file)
        self.clear_table_action.triggered.connect(self.clear_table)
        self.save_file_action.triggered.connect(self.save_file)

    def build_table_context(self, pos):
        self.last_menu_pos = pos
        menu = QtWidgets.QMenu()
        if self.MainTable.rowAt(pos.y()) != -1:
            menu.addAction(self.add_row_action)
            menu.addSeparator()
            menu.addAction(self.delete_row_action)
            menu.addAction(self.clear_table_action)
            menu.addSeparator()
            menu.addAction(self.load_file_action)
            menu.addAction(self.save_file_action)
        else:
            menu.addAction(self.add_row_action)
            menu.addSeparator()
            menu.addAction(self.load_file_action)
            menu.addAction(self.save_file_action)
            menu.addSeparator()
            menu.addAction(self.clear_table_action)
        menu.exec_(self.MainTable.viewport().mapToGlobal(pos))

    def build_main_context(self, pos):
        menu = QtWidgets.QMenu()
        menu.addAction(self.load_file_action)
        menu.addAction(self.save_file_action)
        menu.addSeparator()
        menu.addAction(self.clear_table_action)
        menu.exec_(self.mapToGlobal(pos))

    def delete_row(self):
        self.MainTable.removeRow(self.MainTable.rowAt(self.last_menu_pos.y()))

    def add_row(self):
        rowpos = self.MainTable.rowAt(self.last_menu_pos.y()) + 1
        if rowpos == 0:
            rowpos = self.MainTable.rowCount()
        self.MainTable.insertRow(rowpos)
        for i, placeholder_data in enumerate(("System", "0.00", "0.00", "0")):
            item = QtWidgets.QTableWidgetItem(str(placeholder_data))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.MainTable.setItem(rowpos, i, item)

    def clear_table(self):
        self.MainTable.clearContents()
        self.MainTable.setRowCount(0)
        self.MainTable.horizontalHeaderItem(3).setText("Jumps")

    def load_file(self):
        enter = True
        if self.MainTable.rowCount():
            clear_msg_box = QtWidgets.QMessageBox(icon=QtWidgets.QMessageBox.Information,
                                                  text="Current data will be cleared, continue?",)
            clear_msg_box.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
            # check if clicked button was Yes
            enter = clear_msg_box.exec_() == 16384
        if enter:
            self.MainTable.clearContents()
            self.MainTable.setRowCount(0)
            file, _ = QtWidgets.QFileDialog().getOpenFileName(filter="CSV files (*.csv)")
            if file:
                file = Path(file)
                error_box = QtWidgets.QMessageBox(icon=QtWidgets.QMessageBox.Warning,
                                                  text="Invalid file")
                error_box.setInformativeText(f"The file {file.name} is not a valid CSV file ")
                with file.open(encoding="utf-8") as csvfile:
                    csv_reader = csv.DictReader(csvfile, delimiter=",")
                    try:
                        next(csv_reader)
                    except UnicodeDecodeError:
                        error_box.exec_()
                    else:
                        self.MainTable.itemChanged.disconnect()
                        for rows, row in enumerate(csv_reader):
                            try:
                                datas =(
                                    row['System Name'],
                                    round(float(row['Distance To Arrival']), 2),
                                    round(float(row['Distance Remaining']), 2),
                                    int(row['Jumps']))
                            except (KeyError, ValueError, TypeError):
                                error_box.exec_()
                                break
                            else:
                                self.MainTable.setRowCount(rows + 1)
                                for cindex, column in enumerate(datas):
                                    item = QtWidgets.QTableWidgetItem(str(column))
                                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                                    self.MainTable.setItem(rows, cindex, item)
                        else:
                            self.MainTable.resizeColumnToContents(0)
                            self.update_jumps()

                        self.MainTable.itemChanged.connect(self.changed, QtCore.Qt.UniqueConnection)

    def save_file(self):
        topsys = self.MainTable.item(0, 0)
        bottomsys = self.MainTable.item(self.MainTable.rowCount()-1, 0)

        filename = (f"{topsys.text()}-{bottomsys.text()}.csv".replace("*", "")
                    if topsys and bottomsys else "built_route.csv")
        path, _ = QtWidgets.QFileDialog().getSaveFileName(self,
                                                          filter="CSV files (*.csv)",
                                                          dir=str(filename))
        if path:
            path = Path(path)
            with path.open("w", encoding="UTF-8", newline="") as writefile:
                csvwriter = csv.writer(writefile)
                csvwriter.writerow(("System Name", "Distance To Arrival",
                                    "Distance Remaining", "Jumps"))
                for row in range(self.MainTable.rowCount()):
                    csvwriter.writerow((self.MainTable.item(row, i).text() for i in range(4)))

    def localize(self):
        self.MainTable.horizontalHeaderItem(0).setText("System Name")
        self.MainTable.horizontalHeaderItem(1).setText("Distance")
        self.MainTable.horizontalHeaderItem(2).setText("Remaining")
        self.MainTable.horizontalHeaderItem(3).setText("Jumps")

class CrashPop(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel()
        self.text_browser = QtWidgets.QTextBrowser()
        self.quit_button = QtWidgets.QPushButton()
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(400, 250)
        self.label.setText("An unexpected error has occurred")
        self.quit_button.setText("Quit")
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)

        self.quit_button.pressed.connect(sys.exit)
        self.quit_button.setMaximumWidth(125)
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.text_browser)
        self.main_layout.addWidget(self.quit_button, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(self.main_layout)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setModal(True)

    def add_traceback(self, tcb):
        for line in tcb:
            self.text_browser.append(line)
