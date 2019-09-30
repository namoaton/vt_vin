from PyQt5 import QtCore, QtGui, QtWidgets

from Kassa_tools.tools import make_request, write_to_db


class Postachalnik(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setMinimumSize(QtCore.QSize(480, 80))
        self.setWindowTitle("Додати постачальника")
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        self.newfont = QtGui.QFont("Arial", 24, QtGui.QFont.Bold)

        self.old_postach_label = QtWidgets.QLabel('Обраний постачальник')
        self.old_postach_label.setFont(self.newfont)
        self.old_postach = QtWidgets.QComboBox()
        postach_list = self.get_postach()
        self.old_postach.addItems(postach_list)
        self.old_postach.setFont(self.newfont)

        self.postachalnik_completer = QtWidgets.QCompleter(postach_list)
        self.postachalnik_completer.setCaseSensitivity(
            QtCore.Qt.CaseInsensitive)

        self.new_postach_label = QtWidgets.QLabel('Замінити на :')
        self.new_postach_label.setFont(self.newfont)
        self.new_postach = QtWidgets.QLineEdit()
        self.new_postach.setFont(self.newfont)
        self.new_postach.setCompleter(self.postachalnik_completer)

        self.write_button = QtWidgets.QPushButton('Виконати заміну')
        self.write_button.setFont(self.newfont)

        lbox = QtWidgets.QVBoxLayout()
        lbox.addWidget(self.old_postach_label)
        lbox.addWidget(self.new_postach_label)
        rbox = QtWidgets.QVBoxLayout()
        rbox.addWidget(self.old_postach)
        rbox.addWidget(self.new_postach)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addLayout(lbox)
        hbox.addLayout(rbox)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.write_button)
        self.write_button.clicked.connect(self.replace_postach)
        central_widget.setLayout(vbox)

    def show(self):
        super().show()
        self.reload_postach()

    def get_postach(self):
        postach_list = []
        query = "SELECT `kontragent` FROM `vydacha` "
        results = make_request(query)
        for result in results:
            if result[0] not in postach_list :
                postach_list.append(result[0])
        print(postach_list)
        return postach_list


    def reload_postach(self):
        postach_list = self.get_postach()
        postach_list.sort()
        self.old_postach.clear()
        self.old_postach.addItems(postach_list)
        self.postachalnik_completer = QtWidgets.QCompleter(postach_list)
        self.postachalnik_completer.setCaseSensitivity(
            QtCore.Qt.CaseInsensitive)
        self.new_postach.setCompleter(self.postachalnik_completer)

    def replace_postach(self):
        old_postach = self.old_postach.currentText().replace('"','\"')
        new_postach = self.new_postach.text().replace('"','\"')
        print(old_postach,new_postach)
        query = "UPDATE vydacha SET kontragent='%s' WHERE kontragent='%s'"%(new_postach,old_postach)
        print(query)
        write_to_db(query)
        self.new_postach.setText("")
        self.reload_postach()
