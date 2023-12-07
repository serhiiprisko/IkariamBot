
from botdialog_ui import Ui_BotDialog
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import pyqtSlot

from settings import Settings, UserData


class BotDialog(QDialog, Ui_BotDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    @pyqtSlot()
    def on_pb_ok_clicked(self):
        if self.m_index < 0:
            Settings.addUser(UserData(self.le_username.text(),
                             self.le_password.text(), self.le_proxy.text()))
        else:
            Settings.editUser(self.m_index, UserData(self.le_username.text(),
                                                     self.le_password.text(), self.le_proxy.text()))
        self.accept()

    @pyqtSlot()
    def on_pb_cancel_clicked(self):
        self.reject()

    def addUser(self):
        self.m_index = -1
        self.runDialog()

    def editUser(self, index):
        self.m_index = index
        self.runDialog()

    def runDialog(self):
        if self.m_index < 0:
            self.setWindowTitle("Add User")
        else:
            self.setWindowTitle("Edit User")

            data = Settings.getUser(self.m_index)
            self.le_username.setText(data.username)
            self.le_password.setText(data.password)
            self.le_proxy.setText(data.proxy)

        self.exec()
