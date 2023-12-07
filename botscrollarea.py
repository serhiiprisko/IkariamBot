
from PyQt6.QtWidgets import QScrollArea

from settings import Settings
from botitem import BotItem


class BotScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.botList = []

    def refresh(self):
        self.clear()
        list = Settings.getUsers()
        for i in range(len(list)):
            item = BotItem(self.m_content)
            item.setVisible(True)
            item.setItem(list[i])
            item.m_index = i
            item.m_parent = self

            self.botList.append(item)

        self.updateUI()

    def clear(self):
        for i in range(len(self.botList)):
            item = self.botList[i]
            item.m_thread.stop()
            item.setParent(None)
        self.botList.clear()

    def updateUI(self):
        size = len(self.botList)
        self.m_content.setFixedSize(self.width(), 96 * size)

        for i in range(size):
            item = self.botList[i]
            item.resize(self.width() - 24, 96)
            item.move(0, 96 * i)

    def resizeEvent(self, event):
        self.updateUI()
