import sqlite3
from config import DATABASE_PATH

def connect():
    DATABASE_PATH.parent.mkdir(exist_ok=True, parents=True)
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            asset TEXT, thesis TEXT, setup TEXT, risk TEXT, outcome TEXT
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            title TEXT, body TEXT
        )""")

def add_journal(asset, thesis, setup, risk, outcome=''):
    init_db()
    with connect() as con:
        con.execute('INSERT INTO journal(asset, thesis, setup, risk, outcome) VALUES(?,?,?,?,?)', (asset, thesis, setup, risk, outcome))

def list_journal():
    init_db()
    with connect() as con:
        return con.execute('SELECT created_at, asset, thesis, setup, risk, outcome FROM journal ORDER BY id DESC').fetchall()
