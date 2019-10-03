from PyQt5 import QtWidgets, QtGui, QtCore

from Kassa_tools.tools import edit_transaction, add_transaction, transaction_type, write_to_db, get_kontragents


class Transaction(object):
    """
    Describes typical transaction
    """
    comm = None

    def __init__(self,
                 data=0,
                 kontragent="",
                 summa=0,
                 op_type=0,
                 zvit=0,
                 annot="",
                 t_id=0,
                 stattya_vytrat="",
                 com_event=None):
        super(Transaction, self).__init__()
        self.data = data
        self.kontragent = kontragent
        self.stattya_vytrat = stattya_vytrat
        self.summa = summa
        self.op_type = op_type
        self.zvit = zvit
        self.annot = annot
        self.t_id = t_id
        self.current_money = 0
        comm = com_event

    def print(self):
        print("Operation ", self.data, self.kontragent, self.summa,
              self.op_type, self.zvit, self.stattya_vytrat)

    def operate(self):
        if self.op_type == 0:
            self.add()
        if self.op_type == 1:
            self.withdraw()
        if self.op_type == 2:
            self.withdraw()
        if self.op_type == 3:
            self.make_withdraw()
        if self.op_type == 4:
            self.make_withdraw()
        if self.op_type == 5:
            self.make_withdraw()
        if self.op_type == 6:
            self.withdraw()

    def add(self):
        print("+++++")
        self.current_money = self.current_money + self.summa

    def withdraw(self):
        print("----")
        self.current_money = self.current_money - self.summa

    def make_withdraw(self):
        self.op_type = 2


class AddTransaction(QtWidgets.QMainWindow):
    def __init__(self, parent=None, op_type=0, edit=0, t_id=0):
        super().__init__(parent)
        self.op_type = op_type
        self.edit = edit
        self.id = t_id
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Додати запис")
        if self.edit:
            self.setWindowTitle("Редагувати запис")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Times", 12, QtGui.QFont.Bold)

        self.date_label = QtWidgets.QLabel('Дата')
        self.date_label.setFont(self.newfont)
        self.datetime = QtWidgets.QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QtCore.QDateTime.currentDateTime())
        self.datetime.setFont(self.newfont)

        self.kontragent_name_label = QtWidgets.QLabel('Контрагент')
        self.kontragent_name_label.setFont(self.newfont)
        self.kontragent_name = QtWidgets.QLineEdit()
        self.kontragent_name.setFont(self.newfont)
        self.input_completer = QtWidgets.QCompleter(get_kontragents())
        self.input_completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.kontragent_name.setCompleter(self.input_completer)
        self.stattya_vytrat_label = QtWidgets.QLabel('Стаття витрат')
        self.stattya_vytrat_label.setFont(self.newfont)
        self.stattya_vytrat = QtWidgets.QLineEdit()
        self.stattya_vytrat.setFont(self.newfont)
        self.summa_label = QtWidgets.QLabel('Сума')
        self.summa_label.setFont(self.newfont)
        self.summa = QtWidgets.QLineEdit()
        self.summa.setFont(self.newfont)
        self.annot_label = QtWidgets.QLabel('Примітка')
        self.annot_label.setFont(self.newfont)
        self.annot = QtWidgets.QLineEdit()
        self.annot.setFont(self.newfont)
        self.op_type_label = QtWidgets.QLabel('Тип операції')
        self.op_type_label.setFont(self.newfont)
        self.op_type_tr = QtWidgets.QLabel(transaction_type[self.op_type])
        self.op_type_tr.setFont(self.newfont)
        # self.contact = QtWidgets.QLineEdit()
        # self.contact.setFont(self.newfont)
        if self.edit:
            self.write_button = QtWidgets.QPushButton('Змінити')
        else:
            self.write_button = QtWidgets.QPushButton('Додати')
        self.write_button.setFont(self.newfont)
        v_box_0 = QtWidgets.QVBoxLayout()
        v_box_0.addWidget(self.op_type_label)
        v_box_0.addWidget(self.date_label)
        v_box_0.addWidget(self.stattya_vytrat_label)
        v_box_0.addWidget(self.kontragent_name_label)
        v_box_0.addWidget(self.summa_label)
        v_box_0.addWidget(self.annot_label)
        v_box_1 = QtWidgets.QVBoxLayout()
        v_box_1.addWidget(self.op_type_tr)
        v_box_1.addWidget(self.datetime)
        v_box_1.addWidget(self.stattya_vytrat)
        v_box_1.addWidget(self.kontragent_name)
        v_box_1.addWidget(self.summa)
        v_box_1.addWidget(self.annot)

        main_box = QtWidgets.QHBoxLayout()
        main_box.addLayout(v_box_0)
        main_box.addLayout(v_box_1)
        main_box.addWidget(self.write_button)
        # vbox.addLayout(phone_box)
        # vbox.addLayout(contact_box)
        if self.edit:
            self.write_button.clicked.connect(self.edit_tr)
        else:
            self.write_button.clicked.connect(self.write_tr)
        central_widget.setLayout(main_box)

    def change_op_type(self, op_type):
        self.op_type = op_type
        self.op_type_tr.setText(transaction_type[self.op_type])
        if self.op_type == 0:
            self.stattya_vytrat_label.setText('Стаття надходжень')
            return
        self.stattya_vytrat_label.setText('Стаття витрат')

    def change_edit(self, edit):
        self.edit = edit
        # if 0 = create
        # if 1 = update

    def set_id(self, t_id):
        self.id = t_id

    def clear(self):
        self.annot.setText("")
        self.summa.setText("")
        self.kontragent_name.setText("")
        self.stattya_vytrat.setText("")

    def write_tr(self):
        print(" SUMMA", self.summa.text())
        if (self.summa.text() != ""):
            tr = Transaction(
                data=self.datetime.dateTime().toPyDateTime(),
                kontragent=self.kontragent_name.text(),
                summa=float(self.summa.text().replace(",", ".")),
                op_type=self.op_type,
                annot=self.annot.text(),
                stattya_vytrat=self.stattya_vytrat.text())
            if tr.op_type == 3 or tr.op_type == 4:
                tr.zvit = 1
            tr.print()
            add_transaction(tr)
            self.clear()

    def edit_tr(self):
        tr = Transaction(
            data=self.datetime.dateTime().toPyDateTime(),
            # kontragent=self.kontragent_name.text(),
            summa=float(self.summa.text().replace(",", ".")),
            op_type=self.op_type,
            annot=self.annot.text(),
            zvit=0,
            t_id=self.id,
            stattya_vytrat=self.stattya_vytrat.text())
        tr.print()
        edit_transaction(tr, tr.t_id, str(tr.summa), tr.op_type, tr.annot,
                         tr.data, tr.stattya_vytrat)
        self.clear()
        self.close()


class RemoveTransaction(QtWidgets.QMainWindow):
    def __init__(self, parent=None, op_type=0, edit=0, t_id=0):
        super().__init__(parent)
        self.op_type = op_type
        self.edit = edit
        self.id = t_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Видалити запис")
        if self.edit:
            self.setWindowTitle("Видалити запис")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Arial", 12, QtGui.QFont.Bold)
        self.num_label = QtWidgets.QLabel('Номер')
        self.num_label.setFont(self.newfont)
        self.num = QtWidgets.QLineEdit()
        self.num.setFont(self.newfont)
        self.remove_button = QtWidgets.QPushButton('Видалити')
        self.remove_button.setFont(self.newfont)
        v_box_0 = QtWidgets.QHBoxLayout()
        v_box_0.addWidget(self.num_label)
        v_box_0.addWidget(self.num)
        v_box_1 = QtWidgets.QVBoxLayout()
        v_box_1.addLayout(v_box_0)
        v_box_1.addWidget(self.remove_button)
        self.remove_button.clicked.connect(self.remove)
        central_widget.setLayout(v_box_1)

    def remove(self, op_type):
        print("Ok")
        num_to_remove = self.num.text()
        if num_to_remove:
            query = "DELETE FROM %s WHERE id=%s" % ('vydacha', num_to_remove)
            print(query)
            write_to_db(query)
            self.num.setText("")
        Transaction.comm.reload_all.emit()
        self.close()
