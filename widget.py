

import random
from widget_ui import Ui_Widget
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSlot

from settings import Settings
from botdialog import BotDialog


class Widget(QWidget, Ui_Widget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.sa_bots.m_content = self.sa_bots_content
        self.sa_bots.refresh()
        self.cb_randomDelay.stateChanged.connect(
            lambda: self.on_cb_randomDelay_stateChanged(self.cb_randomDelay))

        Settings.widget_inst = self

    @pyqtSlot()
    def on_pb_add_clicked(self):
        dlg = BotDialog(self)
        dlg.addUser()

        self.sa_bots.refresh()

    @pyqtSlot()
    def on_cb_randomDelay_stateChanged(self, b):
        checked = b.isChecked()

        self.widget.setVisible(checked)

    def closeEvent(self, event):
        self.sa_bots.clear()

    def get_delay(self):
        if self.cb_randomDelay.isChecked() == False:
            return 0
        try:
            delay_min = int(self.le_min.text())
            delay_max = int(self.le_max.text())
            if delay_min > delay_max:
                return 0
            return random.randrange(delay_max - delay_min) + delay_min
        except:
            return 0
