from PyQt5.QtCore import QThread, pyqtSignal
from utils import generate_topics

class Worker(QThread):
    taskFinished = pyqtSignal(str, bool)

    def __init__(self, mainWindow):
        QThread.__init__(self)
        self.mainWindow = mainWindow

    def run(self):
        try:
            topics_list = self.mainWindow.generate_topics()
            self.mainWindow.show_topics_list(topics_list)
            self.mainWindow.postToWordPress(topics_list)
            self.taskFinished.emit("[Result] Task completed successfully.", True)
        except Exception as err:
            self.taskFinished.emit(str(err), False)
