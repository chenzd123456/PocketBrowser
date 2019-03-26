from PyQt5.QtWidgets import QApplication

from View import MainWindow


class PocketBrowser(object):
    def __init__(self):
        self._cmd_map = {
            "open": self._open_url,  # 在当前标签页打开url
            "o": self._open_url,  # 在当前标签页打开url
            "opentab": self._open_url_new_tab,  # 在新标签页打开url
            "ot": self._open_url_new_tab,  # 在新标签页打开url
            "close": self._close,  # 关闭标签页
            "c": self._close,  # 关闭标签页
            "closeother": self._closeOther,  # 关闭其他标签页
            "co": self._closeOther,  # 关闭其他标签页
            "closeleft": self._closeLeft,  # 关闭左侧标签页
            "cl": self._closeLeft,  # 关闭左侧标签页
            "closeright": self._closeRight,  # 关闭右侧标签页
            "cr": self._closeRight,  # 关闭右侧标签页
            "quit": self._quit,  # 退出浏览器
            "q": self._quit  # 退出浏览器
        }

    def run(self, argv):
        app = QApplication(argv)
        self._main_window = MainWindow()
        self._main_window.statusBar().console_bar.returnPressed.connect(
            lambda: self._exec(self._main_window.statusBar().console_bar.text()))
        self._main_window.setWebViewFocus()
        self._main_window.show()
        return app.exec_()

    def _exec(self, cmd):
        self._main_window.statusBar().setCmdMode(False)
        self._main_window.statusBar().console_bar.clear()
        self._main_window.setWebViewFocus()

        token_list = cmd.split()
        try:
            self._cmd_map[token_list[0]](token_list[1:])
        except:
            self._main_window.statusBar().showMessage("commmand error", 5000)

    def _open_url(self, args_list):
        self._main_window.centralWidget().openUrlCurrentTab(args_list[0])

    def _open_url_new_tab(self, args_list):
        self._main_window.centralWidget().addOneTabFore(args_list[0])

    def _close(self, args_list):
        self._main_window.centralWidget().closeCurrentTab()

    def _quit(self, args_list):
        self._main_window.close()

    def _closeOther(self, args_list):
        self._main_window.centralWidget().closeOtherTab()

    def _closeLeft(self, args_list):
        self._main_window.centralWidget().closeLeftTab()

    def _closeRight(self, args_list):
        self._main_window.centralWidget().closeRightTab()