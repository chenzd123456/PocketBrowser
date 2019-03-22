import sqlite3
import sys
import threading

from PyQt5.QtCore import QSize, Qt, QUrl, QPoint
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWidgets import (QAction, QApplication, QLineEdit, QMainWindow,
                             QShortcut, QTabWidget, QToolBar, QToolTip)

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


class WebWindow(QTabWidget):
    "浏览器窗口"

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._tab_list = []

        self.setWindowTitle("PocketBrowser")

        self.setMovable(True)
        self.setTabsClosable(True)
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
        # 按F11全屏
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self._showFullScreen)
        # 按ESC退出全屏
        normalscreen_shortcut = QShortcut(QKeySequence("ESCAPE"), self)
        normalscreen_shortcut.activated.connect(self._showNormalScreen)
        # 按CTRL+N新建标签页
        new_tab_shortcut = QShortcut(QKeySequence("CTRL+N"), self)
        new_tab_shortcut.activated.connect(self._addOneTabFore)

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

    def _addOneTab(self, url=None):
        "添加一个标签页"
        if url == None:
            url = Config().init_page_url
        tab = WebTab(url=url)
        self.addTab(tab, url)
        tab.windowTitleChanged.connect(
            lambda title: self.setTabText(self.count() - 1, title))

    def _addOneTabFore(self, url=None):
        "前台添加一个标签页"
        self._addOneTab(url)
        self.setCurrentIndex(self.count() - 1)

    def _delOneTab(self, index):
        "删除一个标签页"
        self.removeTab(index)
        if self.count() == 0:
            self.close()


class WebTab(QMainWindow):
    "浏览器页面"

    def __init__(self, url=None, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        if url != None:
            self._webview = WebView(QUrl(url))

        self._webview.urlChanged.connect(self._urlChanged)
        self._webview.loadProgress.connect(self._loadProgress)
        self._webview.loadFinished.connect(self._loadFinished)
        self._webview.titleChanged.connect(self._titleChanged)

        self._toolbar = ToolBar()
        self._toolbar.back_button.triggered.connect(self._webview.back)
        self._toolbar.next_button.triggered.connect(self._webview.forward)
        self._toolbar.stop_button.triggered.connect(self._webview.stop)
        self._toolbar.reload_button.triggered.connect(self._webview.reload)
        self._toolbar.url_bar.returnPressed.connect(self._navToUrl)
        self._toolbar.go_button.triggered.connect(self._navToUrl)

        self.addToolBar(self._toolbar)
        self.setCentralWidget(self._webview)

        #### 快捷键 ####
        # 按CTRL+G焦点跳转到地址栏
        urlbar_shortcut = QShortcut(QKeySequence("CTRL+G"), self)
        urlbar_shortcut.activated.connect(self._toolbar.url_bar.setFocus)
        # 按F5刷新页面
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self._webview.reload)

    def _navToUrl(self):
        "跳转网页"
        url = self._toolbar.url_bar.text()
        qurl = QUrl(url)
        if qurl.scheme() == '':
            qurl.setScheme('http')
        self._webview.setUrl(qurl)

    def _urlChanged(self, qurl):
        "url改变"
        url = qurl.toString()
        self._toolbar.url_bar.setText(url)
        self.setWindowTitle(url)
        History().add_history(url)

    def _loadProgress(self, percent):
        "加载进度改变"
        title = self._webview.title()
        self.setWindowTitle("[{}%]{}".format(percent, title))

    def _loadFinished(self):
        "加载完成"
        title = self._webview.title()
        self.setWindowTitle(title)

    def _titleChanged(self, title):
        "标题变化"
        self.setWindowTitle(title)
        History().update_history_title(self._webview.url().toString(), title)


class UrlBar(QLineEdit):
    "地址栏"

    def __init__(self, str="", parent=None):
        super().__init__(str, parent=parent)


class ToolBar(QToolBar):
    "工具栏"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMovable(False)
        self.setIconSize(QSize(16, 16))
        # self.setFixedHeight(28)

        self._back_button = QAction(QIcon('icons/arrowleft.png'), 'Back', self)
        self._next_button = QAction(
            QIcon('icons/arrowright.png'), 'Forward', self)
        self._stop_button = QAction(
            QIcon('icons/close-circle.png'), 'Stop', self)
        self._reload_button = QAction(
            QIcon('icons/reload.png'), 'Reload', self)
        self._url_bar = UrlBar()
        self._go_button = QAction(QIcon('icons/enter.png'), 'Go', self)
        self._favorite_button = QAction(
            QIcon('icons/star.png'), 'Favorite', self)
        self._fullscreen_button = QAction(
            QIcon('icons/fullscreen.png'), 'Favorite', self)
        self._menu_button = QAction(QIcon('icons/menu.png'), 'Menu', self)

        self.addAction(self._back_button)
        self.addAction(self._next_button)
        self.addAction(self._stop_button)
        self.addAction(self._reload_button)
        self.addSeparator()
        self.addWidget(self._url_bar)
        self.addAction(self._go_button)
        self.addSeparator()
        self.addAction(self._favorite_button)
        self.addAction(self._fullscreen_button)
        self.addAction(self._menu_button)

    @property
    def back_button(self):
        return self._back_button

    @property
    def next_button(self):
        return self._next_button

    @property
    def stop_button(self):
        return self._stop_button

    @property
    def reload_button(self):
        return self._reload_button

    @property
    def url_bar(self):
        return self._url_bar

    @property
    def go_button(self):
        return self._go_button

    @property
    def favorite_button(self):
        return self._favorite_button

    @property
    def fullscreen_button(self):
        return self._fullscreen_button

    @property
    def menu_button(self):
        return self._menu_button


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
    main_window = WebWindow()
    main_window.show()
    sys.exit(app.exec_())
