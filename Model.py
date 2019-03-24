import sqlite3
import threading

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
