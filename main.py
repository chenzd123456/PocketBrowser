import sqlite3
import sys
import threading

from PyQt5.QtCore import QSize, Qt, QUrl, QPoint
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWidgets import (QAction, QApplication, QLineEdit, QMainWindow,
                             QShortcut, QTabWidget, QToolBar, QToolTip, QStatusBar)

SQL_CMD = {
    "CREATE_TALBE_HISTORY": "CREATE TABLE IF NOT EXISTS history ( \
        id INTEGER PRIMARY KEY AUTOINCREMENT, \
        url TEXT NOT NULL, \
        title TEXT NOT NULL, \
        time TimeStamp NOT NULL DEFAULT CURRENT_TIMESTAMP)",
    "ADD_HISTORY": "INSERT INTO history (url, title) VALUES (?,?);",
    "READ_HISTORY": "SELECT * FROM history;",
    "CLEAN_HISTORY": "DROP TABLE history;",
    "UPDATE_HISTORY_TITLE": "UPDATE history SET title = ? WHERE url = ? ORDER BY id DESC LIMIT 1 ",
}


class History(object):
    "历史记录"
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(History, "_instance"):
            with History._instance_lock:
                if not hasattr(History, "_instance"):
                    History._instance = object.__new__(cls)
        return History._instance

    def __init__(self):
        self._db_conn = sqlite3.connect("history.db")
        db_cur = self._db_conn.cursor()
        db_cur.execute(SQL_CMD["CREATE_TALBE_HISTORY"])
        self._db_conn.commit()

    def __del__(self):
        self._db_conn.close()

    def add_history(self, url, title=""):
        db_cur = self._db_conn.cursor()
        db_cur.execute(SQL_CMD["ADD_HISTORY"], (url, title))
        self._db_conn.commit()

    def get_history(self):
        db_cur = self._db_conn.cursor()
        result = db_cur.execute(SQL_CMD["READ_HISTORY"])
        return result

    def clean_history(self):
        db_cur = self._db_conn.cursor()
        db_cur.execute(SQL_CMD["CLEAN_HISTORY"] +
                       SQL_CMD["CREATE_TALBE_HISTORY"])
        self._db_conn.commit()

    def update_history_title(self, url, title):
        db_cur = self._db_conn.cursor()
        db_cur.execute(SQL_CMD["UPDATE_HISTORY_TITLE"], (title, url))
        self._db_conn.commit()

class MainWindow(QMainWindow):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        tab_web_widget = TabWebWidget(self)
        status_bar = StatusBar()

        self.setCentralWidget(tab_web_widget)
        self.setStatusBar(status_bar)

        #### 快捷键 ####
        # 按F11全屏
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self._showFullScreen)
        # 按ESC退出全屏
        normalscreen_shortcut = QShortcut(QKeySequence("ESCAPE"), self)
        normalscreen_shortcut.activated.connect(self._showNormalScreen)

    def _swithFullScreen(self):
        "切换全屏"
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _showFullScreen(self):
        "全屏"
        self.showFullScreen()
        # height = self.height()
        # width = self.width()
        # QToolTip.showText(QPoint(width/2, height/2), "ESC")

    def _showNormalScreen(self):
        "退出全屏"
        self.showNormal()

class TabWebWidget(QTabWidget):
    "多标签浏览器控件"

    def __init__(self, top, parent=None):
        super().__init__(parent=parent)
        
        self._top = top

        # self.setMovable(True)
        # self.setTabsClosable(True)
        self.setElideMode(Qt.ElideRight)
        # self.tabBar().setExpanding(True)
        # 当只有一个标签的时候隐藏标签
        # self.setTabBarAutoHide(True)
        # 设置关闭标签后的行为 Qt.SelectLeftTab, Qt.SelectRightTab, Qt.SelectPreviousTab
        # self.tarBar().setSelectionBehaviorOnRemove(Qt.SelectPreviousTab)

        self._addOneTabFore()

        self.tabBarDoubleClicked.connect(self._delOneTab)
        self.tabCloseRequested.connect(self._delOneTab)

        #### 快捷键 ####
        # 按CTRL+N新建标签页
        new_tab_shortcut = QShortcut(QKeySequence("CTRL+N"), self)
        new_tab_shortcut.activated.connect(self._addOneTabFore)

    def _addOneTab(self, url=None):
        "添加一个标签页"
        if url == None:
            url = Config().init_page_url
        tab = WebView(QUrl(url))
        index = self.addTab(tab, url)

        tab.urlChanged.connect(
            lambda qurl: self.setTabText(index, qurl.toString()))
        tab.titleChanged.connect(
            lambda title: self.setTabText(index, title))
        tab.loadProgress.connect(
            lambda progress: self._top.statusBar().showMessage("Loading {}%".format(progress), 1000))
        tab.loadFinished.connect(
            lambda :self._top.statusBar().showMessage("Load Finished", 1000))

    def _addOneTabFore(self, url=None):
        "前台添加一个标签页"
        self._addOneTab(url)
        self.setCurrentIndex(self.count() - 1)

    def _delOneTab(self, index):
        "删除一个标签页"
        self.removeTab(index)
        if self.count() == 0:
            self._top.close()


class CustomWebPage(QWebPage):
    "配置web页面属性"

    def __init__(self):
        super().__init__()

    def userAgentForUrl(self, url):
        config = Config()
        return config.user_agent


class WebView(QWebView):
    "Web视图"

    def __init__(self, qurl=None):
        super().__init__()
        # 设置浏览器UA
        self.setPage(CustomWebPage())
        # 设置浏览器缩放
        self.setZoomFactor(0.8)
        # 指定打开界面的 URL
        if qurl != None:
            self.setUrl(qurl)
        
        # 按F5刷新页面
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.reload)


class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)



class Config(object):
    "浏览器配置"
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(Config, "_instance"):
            with Config._instance_lock:
                if not hasattr(Config, "_instance"):
                    Config._instance = object.__new__(cls)
        return Config._instance

    def __init__(self):
        self._init_page_url = "https://www.baidu.com"
        self._user_agent = """Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A456 Safari/602.1"""

    @property
    def init_page_url(self):
        return self._init_page_url

    @init_page_url.setter
    def init_page_url(self, url):
        self._init_page_url = url

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, user_agent):
        self._user_agent = user_agent


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
