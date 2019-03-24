import sys

from PyQt5.QtCore import QSize, Qt, QUrl, QPoint
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWidgets import (QApplication, QMainWindow, QShortcut, QTabWidget, QToolBar, QToolTip, QStatusBar, QLabel, QHBoxLayout)

from Model import History, Config


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
            lambda: self._top.statusBar().showMessage("Load Finished", 1000))

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