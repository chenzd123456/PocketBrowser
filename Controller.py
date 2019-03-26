from PyQt5.QtWidgets import QApplication

from View import MainWindow


class PocketBrowser(object):
    def __init__(self):
        self._cmd_map = {
            "open": self._open_url,
            "o": self._open_url,
            "opentab": self._open_url_new_tab,
            "ot": self._open_url_new_tab,
        }

    def run(self, argv):
        app = QApplication(argv)
        self._main_window = MainWindow()
        self._main_window.statusBar().console_bar.returnPressed.connect(
            lambda: self._exec(self._main_window.statusBar().console_bar.text()))
        self._main_window.show()
        return app.exec_()

    def _exec(self, cmd):
        self._main_window.statusBar().setCmdMode(False)
        self._main_window.statusBar().console_bar.clear()

        token_list = cmd.split()
        try:
            self._cmd_map[token_list[0]](token_list[1:])
        except:
            self._main_window.statusBar().showMessage("commmand error", 5000)

    def _open_url(self, args_list):
        try:
            self._main_window.centralWidget().openUrlCurrentTab(args_list[0])
        except:
            raise

    def _open_url_new_tab(self, args_list):
        try:
            self._main_window.centralWidget().addOneTabFore(args_list[0])
        except:
            raise
