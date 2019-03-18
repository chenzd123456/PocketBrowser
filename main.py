#!/usr/bin/python3

import sys

from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebKitWidgets import QWebPage, QWebView
from PyQt5.QtWidgets import (QAction, QApplication,
                             QLineEdit, QMainWindow,
                             QShortcut, QToolBar)


class CustomWebPage(QWebPage):
    def __init__(self):
        super().__init__()

    def userAgentForUrl(self, url):
        config = Config()
        return config.user_agent


class WebView(QWebView):
    def __init__(self, url=None):
        super().__init__()
        # 设置浏览器UA
        self.setPage(CustomWebPage())
        # 设置浏览器缩放
        self.setZoomFactor(0.8)
        # 指定打开界面的 URL
        if url != None:
            self.setUrl(QUrl(url))


class Config(object):
    def __init__(self):
        self._home_page_url = "https://www.baidu.com"
        self._user_agent = """Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A456 Safari/602.1"""

    @property
    def home_page_url(self):
        return self._home_page_url

    @home_page_url.setter
    def home_page_url(self, url):
        self._home_page_url = url

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, user_agent):
        self._user_agent = user_agent


class MainWindow(QMainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._isFullScreen = False

        # 设置浏览器首页
        config = Config()
        self._url = config.home_page_url

        # 设置窗口标题
        self.setWindowTitle("PocketBrowser")
        # 设置窗口图标
        # self.setWindowIcon(QIcon('icons/penguin.png'))
        # 设置窗口大小480*270
        # self.resize(480, 270)
        # self.show()

        # 设置浏览器
        self._webview = WebView(self._url)
        # 添加浏览器到窗口中
        self.setCentralWidget(self._webview)

        # 使用QToolBar创建导航栏，并使用QAction创建按钮
        # 添加
        self._navigation_bar = QToolBar('Navigation')
        self._navigation_bar.setMovable(False)
        # 设定导航栏的高度
        # self._navigation_bar.setFixedHeight(24)
        # 设定图标的大小
        self._navigation_bar.setIconSize(QSize(16, 16))
        # 添加导航栏到窗口中
        self.addToolBar(self._navigation_bar)

        # 添加前进、后退、停止加载和刷新的按钮
        back_button = QAction(QIcon('icons/arrowleft.png'), 'Back', self)
        next_button = QAction(QIcon('icons/arrowright.png'), 'Forward', self)
        stop_button = QAction(QIcon('icons/close-circle.png'), 'Stop', self)
        reload_button = QAction(QIcon('icons/reload.png'), 'Reload', self)

        back_button.triggered.connect(self._webview.back)
        next_button.triggered.connect(self._webview.forward)
        stop_button.triggered.connect(self._webview.stop)
        reload_button.triggered.connect(self._webview.reload)

        # 将按钮添加到导航栏上
        self._navigation_bar.addAction(back_button)
        self._navigation_bar.addAction(next_button)
        self._navigation_bar.addAction(stop_button)
        self._navigation_bar.addAction(reload_button)

        # 添加URL地址栏
        self._urlbar = QLineEdit()
        # 让地址栏能响应回车按键信号
        self._urlbar.returnPressed.connect(self.navigate_to_url)

        self._navigation_bar.addSeparator()
        self._navigation_bar.addWidget(self._urlbar)

        # 地址跳转按钮
        go_button = QAction(QIcon('icons/enter.png'), 'Go', self)
        go_button.triggered.connect(self.navigate_to_url)
        self._navigation_bar.addAction(go_button)

        self._navigation_bar.addSeparator()

        # 加收藏按钮
        favorite_button = QAction(QIcon('icons/star.png'), 'Favorite', self)
        favorite_button.triggered.connect(self._favorite)
        self._navigation_bar.addAction(favorite_button)

        # 全屏按钮
        fullscreen_button = QAction(
            QIcon('icons/fullscreen.png'), 'Favorite', self)
        fullscreen_button.triggered.connect(self._inFullscreen)
        self._navigation_bar.addAction(fullscreen_button)

        # 菜单按钮
        menu_button = QAction(QIcon('icons/menu.png'), 'Menu', self)
        self._navigation_bar.addAction(menu_button)

        # 让浏览器相应url地址的变化
        self._webview.urlChanged.connect(self._updateUrl)
        self._webview.loadProgress.connect(self._updateProgress)
        self._webview.loadFinished.connect(self._finishProgress)

        # 快捷键
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self._swithFullScreen)

        urlbar_shortcut = QShortcut(QKeySequence("CTRL+G"), self)
        urlbar_shortcut.activated.connect(self._urlbarFocus)

        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self._webview.reload)

        homepage_shortcut = QShortcut(QKeySequence("CTRL+H"), self)
        homepage_shortcut.activated.connect(self._navigate_to_homepage)

        self._navigate_to_homepage()

    def _swithFullScreen(self):
        if self._isFullScreen:
            self._outFullscreen()
        else:
            self._inFullscreen()
        self._webview.setFocus()

    def _inFullscreen(self):
        self._navigation_bar.setHidden(True)
        self._isFullScreen = True

    def _outFullscreen(self):
        self._navigation_bar.setHidden(False)
        self._isFullScreen = False

    def _urlbarFocus(self):
        if self._isFullScreen:
            self._swithFullScreen()
        self._urlbar.setFocus()

    def navigate_to_url(self):
        qurl = QUrl(self._urlbar.text())
        if qurl.scheme() == '':
            qurl.setScheme('http')
        self._webview.setUrl(qurl)

    def _navigate_to_homepage(self):
        qurl = QUrl("https://www.baidu.com")
        self._webview.setUrl(qurl)

    def _updateUrl(self, q):
        self._url = q.toString()

    def _updateProgress(self, q):
        self._updateUrlbar("[load " + str(q) + "%]" + self._url)

    def _finishProgress(self, q):
        self._updateUrlbar(self._url)

    def _updateUrlbar(self, text):
        self._urlbar.setText(text)
        self._urlbar.setCursorPosition(0)

    def _favorite(self):
        pass


if __name__ == "__main__":
    # 创建应用
    app = QApplication(sys.argv)
    # 创建主窗口
    window = MainWindow()
    # 显示窗口
    window.show()
    # 运行应用，并监听事件
    app.exec_()
