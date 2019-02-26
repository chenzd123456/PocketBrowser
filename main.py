#!/usr/bin/python3

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebKitWidgets import *
from PyQt5.QtWidgets import *


class CustomWebPage(QWebPage):
    UA = """Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A456 Safari/602.1"""

    def userAgentForUrl(self, url):
        return self.UA


class MainWindow(QMainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._isFullScreen = False

        # 设置窗口标题
        self.setWindowTitle('My Browser')
        # 设置窗口图标
        self.setWindowIcon(QIcon('icons/penguin.png'))
        # 设置窗口大小480*270
        self.resize(480, 270)
        self.show()

        # 设置浏览器
        self._browser = QWebView()
        # 设置浏览器UA
        self._browser.setPage(CustomWebPage())
        self._browser.setZoomFactor(0.8)
        # 设置浏览器首页
        url = 'https://www.baidu.com'
        # 指定打开界面的 URL
        self._browser.setUrl(QUrl(url))
        # 添加浏览器到窗口中
        self.setCentralWidget(self._browser)

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

        # QAction类提供了抽象的用户界面action，这些action可以被放置在窗口部件中
        # 添加前进、后退、停止加载和刷新的按钮
        back_button = QAction(QIcon('icons/arrowleft.png'), 'Back', self)
        next_button = QAction(QIcon('icons/arrowright.png'), 'Forward', self)
        stop_button = QAction(QIcon('icons/close-circle.png'), 'Stop', self)
        reload_button = QAction(QIcon('icons/reload.png'), 'Reload', self)

        back_button.triggered.connect(self._browser.back)
        next_button.triggered.connect(self._browser.forward)
        stop_button.triggered.connect(self._browser.stop)
        reload_button.triggered.connect(self._browser.reload)

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

        #地址跳转按钮
        go_button = QAction(QIcon('icons/enter.png'), 'Go', self)
        go_button.triggered.connect(self.navigate_to_url)
        self._navigation_bar.addAction(go_button)

        self._navigation_bar.addSeparator()

        #加收藏按钮
        favorite_button = QAction(QIcon('icons/star.png'), 'Favorite', self)
        favorite_button.triggered.connect(self.favorite)
        self._navigation_bar.addAction(favorite_button)

        #菜单按钮
        menu_button = QAction(QIcon('icons/menu.png'), 'Menu', self)
        self._navigation_bar.addAction(menu_button)

        # 让浏览器相应url地址的变化
        self._browser.urlChanged.connect(self.renew_urlbar)

        # 快捷键
        self.fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        self.fullscreen_shortcut.activated.connect(self.swithFullScreen)

        self.urlbar_shortcut = QShortcut(QKeySequence("CTRL+G"), self)
        self.urlbar_shortcut.activated.connect(self.urlbarFocus)

        self.refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        self.refresh_shortcut.activated.connect(self._browser.reload)

    def swithFullScreen(self):
        if self._isFullScreen:
            self.outFullscreen()
        else:
            self.inFullscreen()
        self._browser.setFocus()

    def inFullscreen(self):
        self._navigation_bar.setHidden(False)
        self._isFullScreen = False

    def outFullscreen(self):
        self._navigation_bar.setHidden(True)
        self._isFullScreen = True

    def urlbarFocus(self):
        if self._isFullScreen:
            self.swithFullScreen()
        self._urlbar.setFocus()

    def navigate_to_url(self):
        url = QUrl(self._urlbar.text())
        if url.scheme() == '':
            url.setScheme('http')
        self._browser.setUrl(url)

    def renew_urlbar(self, q):
        # 将当前网页的链接更新到地址栏
        self._urlbar.setText(q.toString())
        self._urlbar.setCursorPosition(0)

    def favorite(self):
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
