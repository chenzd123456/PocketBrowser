from PyQt5.QtWidgets import QApplication
from View import MainWindow


class PocketBrowser(object):
    def run(self, argv):
        app = QApplication(argv)
        main_window = MainWindow()
        main_window.show()
        return app.exec_()
