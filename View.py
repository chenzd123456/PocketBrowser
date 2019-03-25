import sys

from PyQt5.QtCore import QPoint, QSize, Qt, QUrl
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                             QShortcut, QStatusBar, QTabWidget, QToolBar,
                             QToolTip, QLineEdit)

from Model import Config, History


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
        fullscreen_shortcut.activated.connect(self._swithFullScreen)
        # 按ESC进入命令模式
        cmd_mode_shortcut = QShortcut(QKeySequence("ESCAPE"), self)
        cmd_mode_shortcut.activated.connect(
            lambda: self.statusBar().setCmdMode(True))

    def keyPressEvent(self, event):
        super().keyPressEvent(event)

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
        # 按F5刷新当前页
        reload_shortcut = QShortcut(QKeySequence("F5"), self)
        reload_shortcut.activated.connect(self._reloadCurrentTab)
        # 按CTRL+LEFT切换前一个标签页
        prev_tab_shortcut = QShortcut(QKeySequence("CTRL+LEFT"), self)
        prev_tab_shortcut.activated.connect(self._prev_tab)
        # 按CTRL+RIGHT切换后一个标签页
        prev_tab_shortcut = QShortcut(QKeySequence("CTRL+RIGHT"), self)
        prev_tab_shortcut.activated.connect(self._next_tab)

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

    def _addOneTabFore(self, url=None):
        "前台添加一个标签页"
        self._addOneTab(url)
        self._switch_tab(self.count() - 1)

    def _delOneTab(self, index):
        "删除一个标签页"
        if self.count() <= 1:
            self._top.close()
        else:
            self.removeTab(index)
        self._bind_current_tab_event()

    def _reloadCurrentTab(self):
        "刷新当前页"
        self.currentWidget().reload()
        self._top.statusBar().showMessage("Reloading ...", 5000)

    def _prev_tab(self):
        "切换前一个标签页"
        if self.count() > 1:
            cur_index = self.currentIndex()

            if cur_index == 0:
                cur_index = self.count() - 1
            else:
                cur_index = cur_index - 1

            self._switch_tab(cur_index)

    def _next_tab(self):
        "切换后一个标签页"
        if self.count() > 1:
            cur_index = self.currentIndex()

            if cur_index == self.count() - 1:
                cur_index = 0
            else:
                cur_index = cur_index + 1

            self._switch_tab(cur_index)

    def _switch_tab(self, index):
        "切换标签页"
        self.setCurrentIndex(index)
        self._bind_current_tab_event()

    def _bind_current_tab_event(self):
        "绑定当前标签页的事件"
        self.currentWidget().loadProgress.connect(
            lambda progress: self._top.statusBar().showMessage("Loading {}%".format(progress), 1000))
        self.currentWidget().loadFinished.connect(
            lambda: self._top.statusBar().showMessage("Load Finished", 1000))


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


class StatusBar(QStatusBar):
    "状态栏"

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # 禁止右下角QSizeGrip部件调整窗口大小

        self._is_cmd_mode = False

        self.setSizeGripEnabled(False)
        self._console = QLineEdit()
        self._console.setVisible(False)
        self._status_label = QLabel()

        self.addPermanentWidget(self._console, True)
        self.addPermanentWidget(self._status_label)
        

        self._updateStatusBar()

        self._console.enterEvent

    @property
    def status_label(self):
        return self._status_label

    def showMessage(self, text, timeout=0):
        if not self._is_cmd_mode:
            super().showMessage(text, timeout)

    def showConsole(self, text):
        if self._is_cmd_mode:
            super().showMessage(text)

    def showStatus(self, text):
        self._status_label.setText(text)

    def isCmdMode(self):
        return self._is_cmd_mode

    def setCmdMode(self, bool_):
        if self._is_cmd_mode != bool_:
            self._is_cmd_mode = bool_
            self._updateStatusBar()

    def _updateStatusBar(self):
        if self._is_cmd_mode:
            self._console.setVisible(True)
            self._console.setFocus()
            self._status_label.setText("[ Command Mode ]")
        else:
            self._console.setVisible(False)
            self._status_label.setText("[ Normal  Mode ]")
