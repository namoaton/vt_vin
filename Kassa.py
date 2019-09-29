import json
import sys

# import win32api
# import win32print
from PyQt5 import QtCore, QtGui, QtWidgets

from Kassa_tools.Check import Check
from Kassa_tools.DateDialogs import *
from Kassa_tools.Report import Report
from Kassa_tools.Transactions import Transaction, AddTransaction
from Kassa_tools.tools import *

# last_money = 1028

class Communicate(QtCore.QObject):
    reload_all = QtCore.pyqtSignal()

comm = Communicate()
last_money = get_last_money()

class MainWindow(QtWidgets.QMainWindow):
    # procDone = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)

        # creating EmailBlast widget and setting it as central
        self.window_widget = Window(parent=self)
        self.setCentralWidget(self.window_widget)
        self.setWindowTitle("КАССА")
        self.setWindowIcon(QtGui.QIcon('recycling.png'))
        # filling up a menu bar
        self.menubar = self.menuBar()
        # self.menu =  QtWidgets.QMenu(self.menubar)
        self.add_menu = self.menubar.addMenu('Надходження')
        self.vydacha_menu = self.menubar.addMenu('Видача')
        self.report_menu = self.menubar.addMenu('Звіти')

        self.add_menu_new = QtWidgets.QAction('Внессення', self)
        self.add_menu_new.triggered.connect(lambda: self.vnesennya(op_type=0))
        self.add_menu_do_vydachi = QtWidgets.QAction('До видачі', self)
        self.add_menu_do_vydachi.triggered.connect(
            lambda: self.vnesennya(op_type=5))

        self.add_menu_povernennya = QtWidgets.QAction('Повернення з підзвіту',
                                                      self)
        self.add_menu_povernennya.triggered.connect(self.vnesennya)
        self.add_menu.addAction(self.add_menu_new)
        self.add_menu.addAction(self.add_menu_do_vydachi)
        self.add_menu.addAction(self.add_menu_povernennya)

        self.vydacha_menu_new = QtWidgets.QAction('Видача', self)
        self.vydacha_menu_new.triggered.connect(
            lambda: self.vydacha(op_type=1))
        self.vydacha_menu_new_tovar = QtWidgets.QAction(
            'Видача за товар', self)
        self.vydacha_menu_new_tovar.triggered.connect(
            lambda: self.vydacha(op_type=2))
        self.vydacha_menu_do_vydachi = QtWidgets.QAction(
            'Видача під звіт', self)
        self.vydacha_menu_do_vydachi.triggered.connect(
            lambda: self.vydacha(op_type=4))
        self.vydacha_menu_tovar_zvit = QtWidgets.QAction(
            'Видача за товар під звіт', self)
        self.vydacha_menu_tovar_zvit.triggered.connect(
            lambda: self.vydacha(op_type=3))
        self.vydacha_menu.addAction(self.vydacha_menu_new)
        self.vydacha_menu.addAction(self.vydacha_menu_do_vydachi)
        self.vydacha_menu.addAction(self.vydacha_menu_new_tovar)
        self.vydacha_menu.addAction(self.vydacha_menu_tovar_zvit)
        # reports
        self.date_vytraty_report_menu = QtWidgets.QAction(
            'Звіт витрати по даті')
        self.period_vytraty_report_menu = QtWidgets.QAction(
            'Звіт витрати за період')
        self.date_tovar_report_menu = QtWidgets.QAction(
            'Звіт видача за товар по даті')
        self.period_tovar_report_menu = QtWidgets.QAction(
            'Звіт видача за товар за період')
        self.date_nadh_report_menu = QtWidgets.QAction(
            'Звіт надходження по даті')
        self.period_nadh_report_menu = QtWidgets.QAction(
            'Звіт надходження за період')

        self.period_polymer_bn_report_menu = QtWidgets.QAction(
            'Звіт полімери бн за період')
        self.date_polymer_bn_report_menu = QtWidgets.QAction(
            'Звіт полімери бн по даті')
        self.period_makul_bn_report_menu = QtWidgets.QAction(
            'Звіт макулатура бн за період')
        self.date_makul_bn_report_menu = QtWidgets.QAction(
            'Звіт макулатура бн под даті')


        self.date_vytraty_report_menu.triggered.connect(
            lambda: self.date_report(1))
        self.period_vytraty_report_menu.triggered.connect(
            lambda: self.period_report(1))
        self.date_tovar_report_menu.triggered.connect(
            lambda: self.date_report(2))
        self.period_tovar_report_menu.triggered.connect(
            lambda: self.period_report(2))
        self.date_nadh_report_menu.triggered.connect(
            lambda: self.date_report(0))
        self.period_nadh_report_menu.triggered.connect(
            lambda: self.period_report(0))

        self.report_menu.addAction(self.date_vytraty_report_menu)
        self.report_menu.addAction(self.period_vytraty_report_menu)
        self.report_menu.addAction(self.date_tovar_report_menu)
        self.report_menu.addAction(self.period_tovar_report_menu)
        self.report_menu.addAction(self.date_nadh_report_menu)
        self.report_menu.addAction(self.period_nadh_report_menu)

        # self.report_menu.addAction(self.date_polymer_bn_report_menu)
        # self.report_menu.addAction(self.period_polymer_bn_report_menu)
        # self.report_menu.addAction(self.date_makul_bn_report_menu)
        # self.report_menu.addAction(self.period_makul_bn_report_menu)
        self.dateDialog = DateDialog()
        self.doubleDateDialog = DoubleDateDialog()
        self.addTransaction = AddTransaction()

    def get_tr_list(self, op_type, db_table, data1=0, data2=0):
        tr_list = []
        if data2 != 0:
            end_date = (
                data2 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            end_date = (
                data1 + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        begin_date = data1.strftime('%Y-%m-%d')
        query = "SELECT * FROM %s WHERE op_type=%d and data >= '%s' AND data<='%s'" % (
            db_table, op_type, begin_date, end_date)
        # print(query)
        results = make_request(query)
        # print(results)
        for result in results:
            tr_list.append(
                Transaction(
                    t_id = result[0],
                    data = '{0:%d-%m-%Y %H:%M}'.format(result[1]),
                    kontragent = result[2],
                    summa = float(result[3]),
                    zvit = int(result[4]),
                    annot = result[5],
                    op_type = int(result[6]),
                    stattya_vytrat = result[7]))
        # print(tr_list)
        return tr_list


    def period_report(self, op_type):
        begin_date, begin_time, end_date, end_time, ok = self.doubleDateDialog.getDateTime(
        )
        if op_type == 0:
            db_table = "nadhodjennya"
        else:
            db_table = "vydacha"
        tr_list = self.get_tr_list(op_type, db_table, begin_date, end_date)
        if ok:
            Report(self, op_type, tr_list).show()

    def date_report(self, op_type):
        begin_date, time, ok = self.dateDialog.getDateTime()
        if op_type == 0:
            db_table = "nadhodjennya"
        else:
            db_table = "vydacha"
        tr_list = self.get_tr_list(op_type, db_table, begin_date)
        if ok:
            Report(self, op_type, tr_list).show()

    def vnesennya(self, op_type):
        print("Внессення")
        self.addTransaction.clear()
        self.addTransaction.change_op_type(op_type)
        self.addTransaction.show()

    def vydacha(self, op_type):
        print("Видача")
        self.addTransaction.clear()
        self.addTransaction.change_op_type(op_type)
        self.addTransaction.show()


class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.table_list = []

        self.newfont = QtGui.QFont("Times", 18, QtGui.QFont.Bold)
        self.newfont_table = QtGui.QFont("Times", 12, QtGui.QFont.Bold)

        self.money_label = QtWidgets.QLabel('Гроші оборотні в касі')
        self.money_label.setFont(self.newfont)

        self.money = QtWidgets.QLabel('0')
        self.money.setFont(self.newfont)

        self.money_vydacha_label = QtWidgets.QLabel('Гроші до видачі')
        self.money_vydacha_label.setFont(self.newfont)

        self.money_vydacha = QtWidgets.QLabel('0')
        self.money_vydacha.setFont(self.newfont)

        self.zalyshok_label = QtWidgets.QLabel()  #('Попередній залишок')
        self.zalyshok_label.setFont(self.newfont)

        self.zalyshok = QtWidgets.QLabel()  #(str(last_money))
        self.zalyshok.setFont(self.newfont)

        self.all_money_label = QtWidgets.QLabel('Залишок в касі')
        self.all_money_label.setFont(self.newfont)

        self.all_money = QtWidgets.QLabel('0')
        self.all_money.setFont(self.newfont)

        self.money_table_label = QtWidgets.QLabel('Гроші до видачі')

        self.money_table_label.setFont(self.newfont_table)

        self.money_vydacha_table = QtWidgets.QTableWidget()
        self.money_vydacha_table.setMinimumHeight(200)
        self.money_vydacha_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.money_vydacha_table.setColumnCount(5)
        self.money_vydacha_table.setRowCount(0)

        self.money_vydacha_table.setHorizontalHeaderLabels(
            ["№", "Дата", "Контрагент", "Сумма", "Примітки"])
        self.money_vydacha_table.resizeColumnsToContents()
        self.money_vydacha_table.resizeRowsToContents()
        self.money_vydacha_header = self.money_vydacha_table.horizontalHeader()
        # self.money_vydacha_header.setResizeMode(QHeaderView.ResizeToContents)
        self.money_vydacha_header.setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.money_vydacha_header.setStretchLastSection(True)
        self.money_vydacha_sum = QtWidgets.QLabel('')
        self.table_list.append(
            [self.money_vydacha_table, self.money_vydacha_sum])
        # self.fill_table(self.money_vydacha_table, self.get_transaction_list(0))
        self.fill_table(self.money_vydacha_table, self.get_do_vidachi())

        self.vytraty_table_label = QtWidgets.QLabel('Витрати')
        self.vytraty_table_label.setFont(self.newfont_table)

        self.vytraty_table = QtWidgets.QTableWidget()
        self.vytraty_table.setMinimumHeight(200)
        self.vytraty_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.vytraty_table.setColumnCount(6)
        self.vytraty_table.setRowCount(0)
        self.vytraty_table.setHorizontalHeaderLabels(
            ["№", "Дата", "Контрагент", "Сумма", "Під звіт", "Примітки"])
        self.vytraty_table.resizeColumnsToContents()
        self.vytraty_table.resizeRowsToContents()
        self.vytraty_header = self.vytraty_table.horizontalHeader()
        # self.vytraty_header.setResizeMode(QHeaderView.ResizeToContents)
        self.vytraty_header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.vytraty_header.setStretchLastSection(True)
        self.vytraty_sum = QtWidgets.QLabel('')
        self.table_list.append([self.vytraty_table, self.vytraty_sum])
        self.fill_table(self.vytraty_table, self.get_vitraty(1, 4))
        # self.fill_table(self.vytraty_table, self.get_transaction_list(0))

        self.nadhodjennya_table_label = QtWidgets.QLabel('Надходження')
        self.nadhodjennya_table_label.setFont(self.newfont_table)

        self.nadhodjennya_table = QtWidgets.QTableWidget()
        self.nadhodjennya_table.setMinimumHeight(200)
        self.nadhodjennya_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.nadhodjennya_table.setColumnCount(5)
        self.nadhodjennya_table.setRowCount(0)
        self.nadhodjennya_table.setHorizontalHeaderLabels(
            ["№", "Дата", "Контрагент", "Сумма", "Примітки"])
        self.nadhodjennya_table.resizeColumnsToContents()
        self.nadhodjennya_table.resizeRowsToContents()
        self.nadhodjennya_header = self.nadhodjennya_table.horizontalHeader()
        # self.nadhodjennya_header.setResizeMode(QHeaderView.ResizeToContents)
        self.nadhodjennya_header.setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.nadhodjennya_header.setStretchLastSection(True)
        self.nadhodjennya_sum = QtWidgets.QLabel('')
        self.table_list.append(
            [self.nadhodjennya_table, self.nadhodjennya_sum])

        self.fill_table(self.nadhodjennya_table, self.get_nadhodjennya())

        self.vytraty_za_tovar_table_label = QtWidgets.QLabel(
            'Витрати за товар')
        self.vytraty_za_tovar_table_label.setFont(self.newfont_table)
        self.vytraty_za_tovar_table = QtWidgets.QTableWidget()
        self.vytraty_za_tovar_table.setMinimumHeight(200)

        self.vytraty_za_tovar_table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.vytraty_za_tovar_table.setColumnCount(6)
        self.vytraty_za_tovar_table.setRowCount(0)
        self.vytraty_za_tovar_table.setHorizontalHeaderLabels(
            ["№", "Дата", "Контрагент", "Сумма", "Під звіт", "Примітки"])
        self.vytraty_za_tovar_table.resizeColumnsToContents()
        self.vytraty_za_tovar_table.resizeRowsToContents()
        self.vytraty_za_tovar_header = self.vytraty_za_tovar_table.horizontalHeader(
        )
        # self.vytraty_za_tovar_header.setResizeMode(QHeaderView.ResizeToContents)
        self.vytraty_za_tovar_header.setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.vytraty_za_tovar_header.setStretchLastSection(True)
        self.vytraty_za_tovar_sum = QtWidgets.QLabel('')
        self.table_list.append(
            [self.vytraty_za_tovar_table, self.vytraty_za_tovar_sum])
        self.fill_table(self.vytraty_za_tovar_table, self.get_vitraty(2, 3))
        # self.fill_table(self.vytraty_za_tovar_table,
        # self.get_transaction_list(0))

        self.set_sum(self.table_list)
        v_box_0 = QtWidgets.QVBoxLayout()
        v_box_0.addWidget(self.money_label)
        v_box_0.addWidget(self.money_vydacha_label)
        v_box_0.addWidget(self.zalyshok_label)
        v_box_0.addWidget(self.all_money_label)
        # v_box_0.addStretch()
        v_box_1 = QtWidgets.QVBoxLayout()
        v_box_1.addWidget(self.money)
        v_box_1.addWidget(self.money_vydacha)
        v_box_1.addWidget(self.zalyshok)
        v_box_1.addWidget(self.all_money)
        # v_box_0.addStretch()

        self.date_do_vydachy_box = QtWidgets.QHBoxLayout()
        self.rb_1day = QtWidgets.QRadioButton("За сьогодні")
        self.rb_1day.setChecked(True)
        self.rb_7day = QtWidgets.QRadioButton("За тиждень")
        self.rb_7day.setChecked(False)
        self.rb_30day = QtWidgets.QRadioButton("За весь час")
        self.rb_30day.setChecked(False)
        self.do_vydachy_group = QtWidgets.QButtonGroup()
        self.do_vydachy_group.addButton(self.rb_1day)
        self.do_vydachy_group.addButton(self.rb_7day)
        self.do_vydachy_group.addButton(self.rb_30day)
        self.do_vydachy_group.setExclusive(True)
        self.do_vydachy_group.setId(self.rb_1day, 1)
        self.do_vydachy_group.setId(self.rb_7day, 2)
        self.do_vydachy_group.setId(self.rb_30day, 3)
        self.date_do_vydachy_box.addWidget(self.money_table_label)
        self.date_do_vydachy_box.addWidget(self.rb_1day)
        self.date_do_vydachy_box.addWidget(self.rb_7day)
        self.date_do_vydachy_box.addWidget(self.rb_30day)

        self.date_vytraty_box = QtWidgets.QHBoxLayout()
        self.rb_vytraty_1day = QtWidgets.QRadioButton("За сьогодні")
        self.rb_vytraty_1day.setChecked(True)
        self.rb_vytraty_7day = QtWidgets.QRadioButton("За тиждень")
        self.rb_vytraty_7day.setChecked(False)
        self.rb_vytraty_30day = QtWidgets.QRadioButton("За місяць")
        self.rb_vytraty_30day.setChecked(False)
        self.vytraty_group = QtWidgets.QButtonGroup()
        self.vytraty_group.addButton(self.rb_vytraty_1day)
        self.vytraty_group.addButton(self.rb_vytraty_7day)
        self.vytraty_group.addButton(self.rb_vytraty_30day)
        self.vytraty_group.setExclusive(True)
        self.vytraty_group.setId(self.rb_vytraty_1day, 1)
        self.vytraty_group.setId(self.rb_vytraty_7day, 2)
        self.vytraty_group.setId(self.rb_vytraty_30day, 3)
        self.date_vytraty_box.addWidget(self.vytraty_table_label)
        self.date_vytraty_box.addWidget(self.rb_vytraty_1day)
        self.date_vytraty_box.addWidget(self.rb_vytraty_7day)
        self.date_vytraty_box.addWidget(self.rb_vytraty_30day)

        h_box_lab = QtWidgets.QHBoxLayout()
        h_box_lab.addLayout(v_box_0)
        h_box_lab.addLayout(v_box_1)
        v_box_main_0 = QtWidgets.QVBoxLayout()
        v_box_main_0.addLayout(h_box_lab)
        v_box_main_0.addLayout(self.date_do_vydachy_box)
        # v_box_main_0.addWidget(self.money_table_label)
        v_box_main_0.addWidget(self.money_vydacha_table)
        v_box_main_0.addWidget(self.money_vydacha_sum)
        # v_box_main_0.addWidget(self.vytraty_table_label)
        v_box_main_0.addLayout(self.date_vytraty_box)
        v_box_main_0.addWidget(self.vytraty_table)
        v_box_main_0.addWidget(self.vytraty_sum)

        self.date_nadhodjennya_box = QtWidgets.QHBoxLayout()
        self.rb_nadhodjennya_1day = QtWidgets.QRadioButton("За сьогодні")
        self.rb_nadhodjennya_1day.setChecked(True)
        self.rb_nadhodjennya_7day = QtWidgets.QRadioButton("За тиждень")
        self.rb_nadhodjennya_7day.setChecked(False)
        self.rb_nadhodjennya_30day = QtWidgets.QRadioButton("За місяць")
        self.rb_nadhodjennya_30day.setChecked(False)
        self.nadhodjennya_group = QtWidgets.QButtonGroup()
        self.nadhodjennya_group.addButton(self.rb_nadhodjennya_1day)
        self.nadhodjennya_group.addButton(self.rb_nadhodjennya_7day)
        self.nadhodjennya_group.addButton(self.rb_nadhodjennya_30day)
        self.nadhodjennya_group.setExclusive(True)
        self.nadhodjennya_group.setId(self.rb_nadhodjennya_1day, 1)
        self.nadhodjennya_group.setId(self.rb_nadhodjennya_7day, 2)
        self.nadhodjennya_group.setId(self.rb_nadhodjennya_30day, 3)
        self.date_nadhodjennya_box.addWidget(self.nadhodjennya_table_label)
        self.date_nadhodjennya_box.addWidget(self.rb_nadhodjennya_1day)
        self.date_nadhodjennya_box.addWidget(self.rb_nadhodjennya_7day)
        self.date_nadhodjennya_box.addWidget(self.rb_nadhodjennya_30day)

        self.date_vytraty_tovar_box = QtWidgets.QHBoxLayout()
        self.rb_vytraty_tovar_1day = QtWidgets.QRadioButton("За сьогодні")
        self.rb_vytraty_tovar_1day.setChecked(True)
        self.rb_vytraty_tovar_7day = QtWidgets.QRadioButton("За тиждень")
        self.rb_vytraty_tovar_7day.setChecked(False)
        self.rb_vytraty_tovar_30day = QtWidgets.QRadioButton("За місяць")
        self.rb_vytraty_tovar_30day.setChecked(False)
        self.vytraty_tovar_group = QtWidgets.QButtonGroup()
        self.vytraty_tovar_group.addButton(self.rb_vytraty_tovar_1day)
        self.vytraty_tovar_group.addButton(self.rb_vytraty_tovar_7day)
        self.vytraty_tovar_group.addButton(self.rb_vytraty_tovar_30day)
        self.vytraty_tovar_group.setExclusive(True)
        self.vytraty_tovar_group.setId(self.rb_vytraty_tovar_1day, 1)
        self.vytraty_tovar_group.setId(self.rb_vytraty_tovar_7day, 2)
        self.vytraty_tovar_group.setId(self.rb_vytraty_tovar_30day, 3)
        self.date_vytraty_tovar_box.addWidget(
            self.vytraty_za_tovar_table_label)
        self.date_vytraty_tovar_box.addWidget(self.rb_vytraty_tovar_1day)
        self.date_vytraty_tovar_box.addWidget(self.rb_vytraty_tovar_7day)
        self.date_vytraty_tovar_box.addWidget(self.rb_vytraty_tovar_30day)

        v_box_main_1 = QtWidgets.QVBoxLayout()
        # v_box_main_1.addWidget(self.nadhodjennya_table_label)
        v_box_main_1.addLayout(self.date_nadhodjennya_box)
        v_box_main_1.addWidget(self.nadhodjennya_table)
        v_box_main_1.addWidget(self.nadhodjennya_sum)
        v_box_main_1.addWidget(self.vytraty_za_tovar_table_label)
        v_box_main_1.addLayout(self.date_vytraty_tovar_box)
        v_box_main_1.addWidget(self.vytraty_za_tovar_table)
        v_box_main_1.addWidget(self.vytraty_za_tovar_sum)
        # self.setLayout(v_box)

        main_box = QtWidgets.QHBoxLayout()
        main_box.addLayout(v_box_main_0)
        main_box.addLayout(v_box_main_1)
        self.setLayout(main_box)
        self.setWindowTitle('Kassa_tools')
        self.setGeometry(300, 300, 300, 200)

        self.set_sum_values()
        self.money_vydacha_table.itemDoubleClicked.connect(
            self.obrobka_do_vydachy)
        self.vytraty_za_tovar_table.itemDoubleClicked.connect(
            self.obrobka_pid_zvit_0)
        self.vytraty_table.itemDoubleClicked.connect(self.obrobka_pid_zvit_1)
        self.edit_transaction = AddTransaction(edit=1)
        self.check_show = Check()
        # self.rb_1day.toggled.connect(lambda:self.btnstate(self.b1))
        # self.rb_7day.toggled.connect(lambda:self.btnstate(self.b1))
        # self.rb_30day.toggled.connect(lambda:self.btnstate(self.b1))
        # self.rb_vytraty_1day.connect(lambda:self.btnstate(self.b1))
        # self.rb_vytraty_7day.connect(lambda:self.btnstate(self.b1))
        # self.rb_vytraty_30day.connect(lambda:self.btnstate(self.b1))
        # self.rb_nadhodjennya_1day.connect(lambda:self.btnstate(self.b1))
        # self.rb_nadhodjennya_7day.connect(lambda:self.btnstate(self.b1))
        # self.rb_nadhodjennya_30day.connect(lambda:self.btnstate(self.b1))
        # self.rb_vytraty_tovar_1day.connect(lambda:self.btnstate(self.b1))
        # self.rb_vytraty_tovar_7day.connect(lambda:self.btnstate(self.b1))
        # self.rb_vytraty_tovar_30day.connect(lambda:self.btnstate(self.b1))
        self.do_vydachy_group.buttonClicked.connect(self.on_click)
        self.vytraty_group.buttonClicked.connect(self.on_click)
        self.nadhodjennya_group.buttonClicked.connect(self.on_click)
        self.vytraty_tovar_group.buttonClicked.connect(self.on_click)

        self.vytraty_za_tovar_table.cellClicked.connect(
            self.cell_was_clicked_0)
        self.money_vydacha_table.cellClicked.connect(self.cell_was_clicked_1)
        # self.kassir.activated.connect(self.onActivated)
        # # self.material.activated.connect(self.onMaterialActivated)
        # # self.get_weight_button.clicked.connect(self.get_weight)
        # self.write_button.clicked.connect(self.write_data)
        # self.entrance_checkbox.stateChanged.connect(self.setEntrance)
        # self.pay_checkbox.stateChanged.connect(self.setPayment)
        # self.pending_car_list.itemDoubleClicked.connect(self.fillData)
        # self.our_cars.itemDoubleClicked.connect(self.fillOurData)
        # self.our_cars_reload_button.clicked.connect(self.our_cars_reload)
        # self.material.returnPressed.connect(self.materialEnterClicked)
        # self.wait_for_archive_button.clicked.connect(self.reload_archive)
        # self.wait_for_archive_table.itemDoubleClicked.connect(self.archiveEdit)
        # self.record = Record.Record()
        # ReadWeightThread(self.weight)
        global comm
        comm.reload_all.connect(self.reload_all)

    def cell_was_clicked_0(self, row, column):
        tmp_list = []
        if column == 5:
            tmp_list = self.vytraty_za_tovar_table.item(
                row, column).text().split(" ")
        if not len(tmp_list):
            return
        self.check_show.set_number(tmp_list[0])
        self.check_show.show()

    def cell_was_clicked_1(self, row, column):
        tmp_list = []
        if column == 4:
            tmp_list = self.money_vydacha_table.item(row,
                                                     column).text().split(" ")
        if not len(tmp_list):
            return
        self.check_show.set_number(tmp_list[0])
        self.check_show.show()

    def show_check(self, tmp_list):
        result = make_weight_request(tmp_list[0])[0]
        print(result[12], result[6])
        check_items = json.loads(result[6])
        check_text = ""
        for key in check_items.keys():
            check_text = check_text + key + " : " + str(
                check_items[key]['weight']) + " : " + str(
                    check_items[key]['price']) + "\n"

        QtWidgets.QMessageBox.about(self, 'Документ %s' % tmp_list[0],
                                    check_text)

    def on_click(self, button):
        period_list[0] = self.do_vydachy_group.checkedId()
        period_list[1] = self.vytraty_group.checkedId()
        period_list[2] = self.nadhodjennya_group.checkedId()
        period_list[3] = self.vytraty_tovar_group.checkedId()
        print(period_list)
        comm.reload_all.emit()

    def obrobka_pid_zvit_0(self):
        row = self.vytraty_za_tovar_table.selectedIndexes()[0].row()
        print(row)
        index = self.vytraty_za_tovar_table.item(row, 0).text()
        summ = self.vytraty_za_tovar_table.item(row, 3).text()
        annot = self.vytraty_za_tovar_table.item(row, 5).text()
        kontragent = self.vytraty_za_tovar_table.item(row, 2).text()
        print(index, summ, annot)
        if self.vytraty_za_tovar_table.item(row, 4).text() == "1":
            self.edit_transaction.set_id(index)
            self.edit_transaction.clear()
            self.edit_transaction.change_op_type(2)
            self.edit_transaction.summa.setText(summ)
            self.edit_transaction.annot.setText(annot)
            self.edit_transaction.kontragent_name.setText(kontragent)
            self.edit_transaction.show()

    def obrobka_pid_zvit_1(self):
        row = self.vytraty_table.selectedIndexes()[0].row()
        print(row)
        index = self.vytraty_table.item(row, 0).text()
        summ = self.vytraty_table.item(row, 3).text()
        annot = self.vytraty_table.item(row, 5).text()
        kontragent = self.vytraty_table.item(row, 2).text()
        print(index, summ, annot)
        if self.vytraty_table.item(row, 4).text() == "1":
            self.edit_transaction.set_id(index)
            self.edit_transaction.clear()
            self.edit_transaction.change_op_type(1)
            self.edit_transaction.summa.setText(summ)
            self.edit_transaction.annot.setText(annot)
            self.edit_transaction.kontragent_name.setText(kontragent)
            self.edit_transaction.show()

    def obrobka_do_vydachy(self):
        row = self.money_vydacha_table.selectedIndexes()[0].row()
        print(row)
        index = self.money_vydacha_table.item(row, 0).text()
        summ = self.money_vydacha_table.item(row, 3).text()
        annot = self.money_vydacha_table.item(row, 4).text()
        kontragent = self.money_vydacha_table.item(row, 2).text()
        print(index, summ, annot)

        self.edit_transaction.set_id(index)
        self.edit_transaction.clear()
        self.edit_transaction.change_op_type(2)
        self.edit_transaction.summa.setText(summ)
        self.edit_transaction.annot.setText(annot)
        self.edit_transaction.kontragent_name.setText(kontragent)
        self.edit_transaction.show()

    def get_period(self, i):
        if i == 1:
            return 0
        if i == 2:
            return 7
        if i == 3:
            return 31

    def u_vytraty(self):
        print("Achive clicked")
        row = self.money_vydacha_table.selectedIndexes()[0].row()
        print(row)
        index = self.money_vydacha_table.item(row, 0).text()
        summ = self.money_vydacha_table.item(row, 3).text()
        print(index)
        write_to_db("UPDATE vydacha SET op_type=2, summa=%s  WHERE id=%s" %
                    (summ, index))
        comm.reload_all.emit()

    def set_sum_values(self):
        global summ_before_period
        global summ_cur_period

        total_sum = summ_cur_period["nadhodjennya"] + summ_before_period["nadhodjennya"]
        print("total_summ", total_sum, summ_before_period["nadhodjennya"],
              summ_cur_period["nadhodjennya"])

        vytraty_sum_period = (summ_before_period["vytraty_za_tovar"] +\
                  summ_before_period["vytraty"])
        vytraty_sum = summ_cur_period["vytraty_za_tovar"] + summ_cur_period["vytraty"]

        vytray_pid_zvit_period = summ_before_period["vytraty_za_tovar_pid_zvit"] +\
                  summ_before_period["vytraty_pid_zvit"]

        vytray_pid_zvit = summ_cur_period["vytraty_za_tovar_pid_zvit"] + \
               summ_cur_period["vytraty_pid_zvit"]

        print("vytraty_sum", vytraty_sum, vytraty_sum_period)
        print("vytray_pid_zvit", vytray_pid_zvit, vytray_pid_zvit_period)

        self.all_money.setText(str(total_sum - vytraty_sum - vytray_pid_zvit -\
         vytray_pid_zvit_period - vytraty_sum_period ))
        self.money_vydacha.setText(str(summ_cur_period["vydacha"] +\
         summ_before_period["vydacha"]))

        self.money.setText(
            str(
                float(self.all_money.text()) - float(self.money_vydacha.text())
            ))

    def set_sum(self, table_list):
        for table in table_list:
            # print(table)
            table[1].setText(self.get_table_summ(table[0]))
            print(self.get_table_summ(table[0]).replace("\n", ":").split(":"))
            # if table[0].columnCount() == 6:
            #     table[1].setText("Під звіт : 100\nПросто : 100 \nУсього : 200")
            # else:
            #     table[1].setText("Усього : 200")

    def get_table_summ(self, table):
        sum_zvit = 0
        sum_other = 0
        sum_total = 0
        for row in range(0, table.rowCount()):
            if table.item(row, 3):
                sum_total = sum_total + float(table.item(row, 3).text())
                if table.columnCount() == 6 and int(table.item(row,
                                                               4).text()) == 1:
                    sum_zvit = sum_zvit + float(table.item(row, 3).text())
        if table.columnCount() == 5:
            return ("Усього: %.2f" % (sum_total))
        return ("Під звіт : %.2f\nПросто : %.2f \nУсього : %.2f" %
                (sum_zvit, sum_total - sum_zvit, sum_total))

    def get_transaction_list(self, op_type):
        tr_list = []
        for i in range(0, 10):
            tr_list.append(
                Transaction(
                    data="20.10.2018",
                    kontragent="Vasya",
                    summa=100 + i,
                    op_type=5,
                    zvit=i % 2,
                    t_id=44))
        return tr_list

    def get_nadhodjennya(self):
        tr_list = []
        period = self.get_period(period_list[2])
        now = datetime.datetime.now() - datetime.timedelta(days=period)
        formatted_date = now.strftime('%Y-%m-%d')

        results = make_request(
            "SELECT * FROM nadhodjennya WHERE data >='%s'" % formatted_date)
        for result in results:
            tr_list.append(
                Transaction(
                    t_id=result[0],
                    data='{0:%d-%m-%Y %H:%M}'.format(result[1]),
                    kontragent=result[2],
                    summa=float(result[3]),
                    zvit=int(result[4]),
                    annot=result[5],
                    op_type=int(result[6])))

        # print(result)
        return tr_list

    def get_do_vidachi(self):
        tr_list = []
        period = self.get_period(period_list[0])
        now = datetime.datetime.now() - datetime.timedelta(days=period)
        formatted_date = now.strftime('%Y-%m-%d')
        query = "SELECT * FROM vydacha WHERE op_type=5 and data>='%s'" % formatted_date
        if period == 31:
            query = ("SELECT * FROM vydacha WHERE op_type=5")
        results = make_request(query)
        for result in results:
            tr_list.append(
                Transaction(
                    t_id=result[0],
                    data='{0:%d-%m-%Y %H:%M}'.format(result[1]),
                    kontragent=result[2],
                    summa=float(result[3]),
                    zvit=int(result[4]),
                    annot=result[5],
                    op_type=int(result[6])))

        # print(result)
        return tr_list

    def get_vitraty(self, op_type_1, op_type_2):
        tr_list = []
        if op_type_1 == 1:
            period = self.get_period(period_list[1])
        if op_type_1 == 2:
            period = self.get_period(period_list[3])
        now = datetime.datetime.now() - datetime.timedelta(days=period)
        formatted_date = now.strftime('%Y-%m-%d')
        results = make_request(
            "SELECT * FROM vydacha WHERE  (op_type=%d or op_type=%d) and data>='%s'"
            % (op_type_1, op_type_2, formatted_date))
        for result in results:
            tr_list.append(
                Transaction(
                    t_id=result[0],
                    data='{0:%d-%m-%Y %H:%M}'.format(result[1]),
                    kontragent=result[2],
                    summa=float(result[3]),
                    zvit=int(result[4]),
                    annot=result[5],
                    op_type=int(result[6])))

        # print(result)
        return tr_list

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
            if table.columnCount() == 5:
                table.setItem(row_count, 4, QtWidgets.QTableWidgetItem(
                    tr.annot))
            else:
                table.setItem(row_count, 4,
                              QtWidgets.QTableWidgetItem(str(tr.zvit)))
                table.setItem(row_count, 5, QtWidgets.QTableWidgetItem(
                    tr.annot))
            row_count = row_count + 1

    def reload_all(self):
        self.clear_table(self.nadhodjennya_table)
        self.fill_table(self.nadhodjennya_table, self.get_nadhodjennya())

        self.clear_table(self.money_vydacha_table)
        self.fill_table(self.money_vydacha_table, self.get_do_vidachi())

        self.clear_table(self.vytraty_table)
        self.fill_table(self.vytraty_table, self.get_vitraty(1, 4))

        self.clear_table(self.vytraty_za_tovar_table)
        self.fill_table(self.vytraty_za_tovar_table, self.get_vitraty(2, 3))

        self.set_sum(self.table_list)
        get_summ_period()
        get_summ_cur()
        self.set_sum_values()

    def clear_table(self, table):
        row_count = table.rowCount()
        for row in range(0, row_count):
            table.removeRow(row)
        table.setRowCount(0)


print("Get before period")
get_summ_period()
print("Get  cur period")
get_summ_cur()
app = QtWidgets.QApplication(sys.argv)
# a_window = Window()
a_window = MainWindow()
a_window.show()
sys.exit(app.exec_())