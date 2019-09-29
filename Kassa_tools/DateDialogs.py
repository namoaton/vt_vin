from PyQt5 import QtCore, QtWidgets


class DateDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DateDialog, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        # nice widget for editing the date
        self.datetime = QtWidgets.QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QtCore.QDateTime.currentDateTime())
        layout.addWidget(self.datetime)
        # OK and Cancel buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current date and time from the dialog
    def dateTime(self):
        return self.datetime.dateTime()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent=None):
        dialog = DateDialog(parent)
        result = dialog.exec_()
        date = dialog.dateTime().toPyDateTime()
        return (date.date(), date.time(), result == QtWidgets.QDialog.Accepted)


class DoubleDateDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(DoubleDateDialog, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        # nice widget for editing the date
        self.begin_time_label = QtWidgets.QLabel("c:")
        self.datetime = QtWidgets.QDateTimeEdit(self)
        self.datetime.setCalendarPopup(False)
        self.datetime.setDateTime(QtCore.QDateTime.currentDateTime())
        self.end_time_label = QtWidgets.QLabel("по")
        self.end_datetime = QtWidgets.QDateTimeEdit(self)
        self.end_datetime.setCalendarPopup(False)
        self.end_datetime.setDateTime(QtCore.QDateTime.currentDateTime())
        layout.addWidget(self.begin_time_label)
        layout.addWidget(self.datetime)
        layout.addWidget(self.end_time_label)
        layout.addWidget(self.end_datetime)
        # OK and Cancel buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current date and time from the dialog
    def dateTime(self):
        return (self.datetime.dateTime(), self.end_datetime.dateTime())

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent=None):
        dialog = DoubleDateDialog(parent)
        result = dialog.exec_()
        print(dialog.dateTime())
        date = dialog.dateTime()[0].toPyDateTime()
        end_date = dialog.dateTime()[1].toPyDateTime()
        return (date.date(), date.time(), end_date.date(), end_date.time(),
                result == QtWidgets.QDialog.Accepted)
