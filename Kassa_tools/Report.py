import csv
from PyQt5 import QtCore, QtWidgets, QtGui

from Kassa_tools.Check import Check
from Kassa_tools.tools import transaction_type


class Report(QtWidgets.QMainWindow):
    def __init__(self, parent=None, op_type=0, tr_list=[]):
        super().__init__(parent)
        self.newfont = QtGui.QFont("Times", 12, QtGui.QFont.Bold)
        self.op_type = op_type
        self.tr_list = tr_list
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(980, 580))
        self.setWindowTitle("Звіт " + transaction_type[self.op_type])
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        self.report_table = QtWidgets.QTableWidget()
        self.report_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.report_table.setColumnCount(6)
        self.report_table.setRowCount(0)

        self.report_table.setHorizontalHeaderLabels(
            ["№", "Дата", "Контрагент", "Сума", "Примітки", "Стаття витрат"])
        self.report_table.resizeColumnsToContents()
        self.report_table.resizeRowsToContents()
        self.report_table.setMinimumHeight(300)
        self.report_table.setMinimumWidth(600)
        self.report_table_header = self.report_table.horizontalHeader()
        # self.report_table_header.setResizeMode(QHeaderView.ResizeToContents)
        self.report_table_header.setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.report_table_header.setStretchLastSection(True)
        self.fill_table(self.report_table, self.tr_list)
        period = self.get_peroid(self.report_table)
        print(period)
        if len(period) == 1:
            self.setWindowTitle(
                "Звіт " + transaction_type[self.op_type] + "за " + period[0])
        else:
            self.setWindowTitle("Звіт " + transaction_type[self.op_type] +
                                " з " + period[0] + " по " + period[1])
        self.summ_label = QtWidgets.QLabel(
            'Cума: ' + self.get_table_summ(self.report_table))
        self.summ_label.setFont(self.newfont)
        self.summ_value = QtWidgets.QLabel()
        self.summ_value.setFont(self.newfont)
        sum_box = QtWidgets.QHBoxLayout()
        sum_box.addWidget(self.summ_label)
        sum_box.addWidget(self.summ_value)
        left_box = QtWidgets.QVBoxLayout()
        left_box.addWidget(self.report_table)
        left_box.addLayout(sum_box)

        right_box = QtWidgets.QVBoxLayout()
        self.kontragent_filter = QtWidgets.QComboBox()
        self.prymytky_filter = QtWidgets.QComboBox()
        self.k_filter_button = QtWidgets.QPushButton("Фільтр контрагента")
        self.p_filter_button = QtWidgets.QPushButton("Фільтр примітки")
        self.csv_button = QtWidgets.QPushButton("Завантажиити CSV")

        self.kontragent_filter.addItems(self.get_kontragent())
        self.prymytky_filter.addItems(self.get_prymytky())
        self.k_filter_button.clicked.connect(self.show_filtered_data_k)
        self.p_filter_button.clicked.connect(self.show_filtered_data_p)
        self.csv_button.clicked.connect(self.download_csv)
        right_box.setAlignment(QtCore.Qt.AlignTop)
        right_box.addWidget(self.kontragent_filter)
        right_box.addWidget(self.k_filter_button)
        right_box.addWidget(self.prymytky_filter)
        right_box.addWidget(self.p_filter_button)
        right_box.addWidget(self.csv_button)
        main_box = QtWidgets.QHBoxLayout()
        main_box.addLayout(left_box)
        main_box.addLayout(right_box)

        central_widget.setLayout(main_box)

        self.check_show = Check()
        self.report_table.cellClicked.connect(self.cell_was_clicked_1)
        self.report_table.itemSelectionChanged.connect(self.cell_was_clicked)

    def show_filtered_data_k(self):
        filtr = str(self.kontragent_filter.currentText())
        temp_list = []
        for t in self.tr_list:
            if filtr == t.kontragent:
                temp_list.append(t)
        Report(self, self.op_type, temp_list).show()

    def show_filtered_data_p(self):
        filtr = str(self.prymytky_filter.currentText())
        temp_list = []
        for t in self.tr_list:
            if filtr == t.annot:
                temp_list.append(t)
        Report(self, self.op_type, temp_list).show()

    def get_kontragent(self):
        k_list = []
        for t in self.tr_list:
            if t.kontragent not in k_list:
                k_list.append(t.kontragent)
        # print(k_list)
        return k_list

    def get_prymytky(self):
        p_list = []
        for t in self.tr_list:
            if t.annot not in p_list:
                p_list.append(t.annot)
        # print(p_list)
        return p_list

    def get_stattya_vytrat(self):
        s_list = []
        for t in self.tr_list:
            if t.statya_vytrat not in s_list:
                s_list.append(t.statya_vytrat)
        # print(p_list)
        return s_list

    def cell_was_clicked(self):
        total_sum = 0
        for item in self.report_table.selectedItems():
            if item.column() == 3:
                print(item.text())
                total_sum = total_sum + float(item.text())
        # item = self.report_table.itemAt(row, column)
        if total_sum:
            self.summ_value.setText("Сумма обраних комірок: %.2f" % total_sum)
        else:
            self.summ_value.setText("")

    def cell_was_clicked_1(self, row, column):
        tmp_list = []
        if column == 4:
            tmp_list = self.report_table.item(row, column).text().split(" ")
        if not len(tmp_list):
            return
        try:
            a = int(tmp_list[0])
        except Exception as e:
            return
        self.check_show.set_number(tmp_list[0])
        self.check_show.show()

    def get_table_summ(self, table):
        sum_total = 0
        for row in range(0, table.rowCount()):
            if table.item(row, 3):
                sum_total = sum_total + float(table.item(row, 3).text())
        return ("%.2f" % (sum_total))

    def get_peroid(self, table):
        data_set = []
        data_set.append(table.item(0, 1).text()[:10])
        data_set.append(table.item(table.rowCount() - 1, 1).text()[:10])
        return data_set
        # return ("%.2f" % (sum_total))

    def fill_table(self, table, tr_list):
        row_count = table.rowCount()
        for tr in tr_list:
            table.insertRow(row_count)
            table.setItem(row_count, 0, QtWidgets.QTableWidgetItem(
                str(tr.t_id)))
            table.setItem(row_count, 1, QtWidgets.QTableWidgetItem(tr.data))
            table.setItem(row_count, 2,
                          QtWidgets.QTableWidgetItem(tr.kontragent))
            table.setItem(row_count, 3,
                          QtWidgets.QTableWidgetItem(str(tr.summa)))
            if table.columnCount() == 6:
                table.setItem(row_count, 4, QtWidgets.QTableWidgetItem(
                    tr.annot))
                table.setItem(row_count, 5, QtWidgets.QTableWidgetItem(
                    tr.stattya_vytrat))
            else:
                table.setItem(row_count, 4,
                              QtWidgets.QTableWidgetItem(str(tr.zvit)))
                table.setItem(row_count, 5, QtWidgets.QTableWidgetItem(
                    tr.annot))
                table.setItem(row_count, 6, QtWidgets.QTableWidgetItem(
                    tr.stattya_vytrat))
            row_count = row_count + 1

    def download_csv(self):
        options = QtWidgets.QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "QFileDialog.getSaveFileName()",
            "",
            " CSV (*.csv);;Все файлы (*)",
            options=options)
        if fileName:
            print(fileName)
            with open(fileName, 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                row_count = 0
                writer.writerow(
                    ["№", "Дата", "Контрагент", "Сума", "Примітки"])
                while row_count != self.report_table.rowCount():
                    row_append = []
                    column_counter = 0
                    while column_counter != 5:
                        row_append.append(
                            self.report_table.item(
                                row_count, column_counter).text().replace(
                                '.', ','))
                        column_counter += 1
                    print(row_append)
                    writer.writerow(row_append)
                    row_count += 1