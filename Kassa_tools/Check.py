from PyQt5 import QtWidgets, QtGui, QtCore

from Kassa_tools.tools import make_weight_request


class Check(QtWidgets.QMainWindow):
    def __init__(self, parent=None, doc_number="one"):
        super().__init__(parent)
        self.doc_number = doc_number

        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(580, 280))
        self.setWindowTitle("Документ " + (str(self.doc_number)))
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Times", 12, QtGui.QFont.Bold)

        self.doc_table = QtWidgets.QTableWidget()
        self.doc_table.setMinimumHeight(200)
        self.doc_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.doc_table.setColumnCount(4)
        self.doc_table.setRowCount(0)
        self.doc_table.setHorizontalHeaderLabels(
            ["Матеріал", "Вага кг", "Вартість/кг", "Сума"])
        self.doc_table.resizeColumnsToContents()
        self.doc_table.resizeRowsToContents()
        self.doc_table.setMinimumHeight(300)
        self.doc_table.setMinimumWidth(300)
        self.doc_table_header = self.doc_table.horizontalHeader()
        # self.doc_table_header.setResizeMode(QHeaderView.ResizeToContents)
        self.doc_table_header.setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.doc_table_header.setStretchLastSection(True)
        if not (self.doc_number == "one"):
            self.fill_table()
        self.summ_value = QtWidgets.QLabel()
        self.summ_value.setFont(self.newfont)

        main_box = QtWidgets.QVBoxLayout()
        main_box.addWidget(self.doc_table)
        main_box.addWidget(self.summ_value)
        central_widget.setLayout(main_box)

    def set_number(self, new_number):
        self.doc_number = new_number
        self.clear_table()
        self.fill_table()
        self.setWindowTitle("Документ " + (str(self.doc_number)))

    def fill_table(self):
        result = make_weight_request(self.doc_number)[0]
        print(result[12], result[6])
        check_items = json.loads(result[6])
        row_count = self.doc_table.rowCount()
        total_sum = 0
        for key in check_items.keys():
            self.doc_table.insertRow(row_count)
            self.doc_table.setItem(row_count, 0,
                                   QtWidgets.QTableWidgetItem(key))
            self.doc_table.setItem(row_count, 1,
                                   QtWidgets.QTableWidgetItem(
                                       str(check_items[key]['weight'])))
            self.doc_table.setItem(row_count, 2,
                                   QtWidgets.QTableWidgetItem(
                                       str(check_items[key]['price'])))
            self.doc_table.setItem(
                row_count, 3,
                QtWidgets.QTableWidgetItem(
                    "%.2f" %
                    (check_items[key]['weight'] * check_items[key]['price'])))
            row_count = row_count + 1
            total_sum = total_sum + (
                check_items[key]['weight'] * check_items[key]['price'])
        self.summ_value.setText(("%.2f" % total_sum) + " грн")

    def clear_table(self):
        row_count = self.doc_table.rowCount()
        for row in range(0, row_count):
            self.doc_table.removeRow(row)
        self.doc_table.setRowCount(0)