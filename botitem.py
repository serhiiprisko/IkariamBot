
from botitem_ui import Ui_BotItem
from PyQt6.QtWidgets import QWidget, QInputDialog
from PyQt6.QtCore import pyqtSlot

from botdialog import BotDialog
from settings import Settings
from bot import Bot


class BotItem(QWidget, Ui_BotItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.m_thread = Bot(self)
        self.m_thread.statusSignal.connect(self.on_status)
        self.m_thread.pointsSignal.connect(self.on_points)
        self.m_thread.finished.connect(self.finished)
        self.pb_collect.setVisible(False)

    def setItem(self, data):
        self.le_username.setText(data.username)
        self.le_password.setText(data.password)
        self.le_proxy.setText(data.proxy)

        self.started(False, False)

    def started(self, control, bot):
        self.pb_stop.setEnabled(control)
        self.pb_start.setEnabled(not control)
        self.pb_testProxy.setEnabled(not control)
        self.w_bot.setVisible(bot)

        if bot == True:
            self.pb_attack.setEnabled(False)
            self.pb_collect.setEnabled(False)
            self.pb_train.setEnabled(False)

    @pyqtSlot()
    def on_pb_edit_clicked(self):
        dlg = BotDialog(self)
        dlg.editUser(self.m_index)

        self.m_parent.refresh()

    @pyqtSlot()
    def on_pb_delete_clicked(self):
        Settings.deleteUser(self.m_index)

        self.m_parent.refresh()

    @pyqtSlot()
    def on_pb_testProxy_clicked(self):
        proxy = self.le_proxy.text()

        self.m_thread.startTest(proxy)
        self.started(True, False)

    @pyqtSlot()
    def on_pb_start_clicked(self):
        username = self.le_username.text()
        password = self.le_password.text()
        proxy = self.le_proxy.text()
        type = self.cb_type.currentIndex()

        self.pb_resume.setVisible(False)
        self.pb_pause.setVisible(True)

        self.m_thread.startBot(username, password, proxy, type)
        self.started(True, True)

    @pyqtSlot()
    def on_pb_stop_clicked(self):
        self.m_thread.stop()

    @pyqtSlot()
    def on_pb_show_clicked(self):
        self.m_thread.show()

    @pyqtSlot()
    def on_pb_hide_clicked(self):
        self.m_thread.hide()

    @pyqtSlot()
    def on_pb_pause_clicked(self):
        self.m_thread.pause()
        self.pb_pause.setVisible(False)
        self.pb_resume.setVisible(True)

    @pyqtSlot()
    def on_pb_resume_clicked(self):
        self.m_thread.resume()
        self.pb_pause.setVisible(True)
        self.pb_resume.setVisible(False)

    # @pyqtSlot()
    # def on_pb_collect_clicked(self):
    #    self.m_thread.action = "collect"

    @pyqtSlot()
    def on_pb_train_clicked(self):
        number, ok = QInputDialog().getInt(self, "Input number to train",
                                           "Numbers", 0)
        if ok and number > 0:
            self.m_thread.train(number)

    @pyqtSlot()
    def on_pb_attack_clicked(self):
        text, ok = QInputDialog().getText(self, "Input username to attack",
                                          "Username:")
        if ok and text:
            self.m_thread.attack(text)

    @pyqtSlot(str)
    def on_status(self, text):
        self.l_status.setText(text)

        if text == 'Take your actions':
            self.pb_attack.setEnabled(True)
            self.pb_collect.setEnabled(True)
            self.pb_train.setEnabled(True)

    @pyqtSlot(str, str)
    def on_points(self, piracy, crew):
        self.l_points.setText("Piracy points: " +
                              str(piracy) + "    Crew points: " + str(crew))

    def finished(self):
        self.started(False, False)
        self.m_thread.m_isRunning = False
