import sqlite3


def settup():
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS request_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request TEXT NOT NULL UNIQUE,
            body TEXT,
            creation_date timestamp);
        ''')


def write(request, body, creation_date):
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute('''INSERT or REPLACE INTO request_history
            ('request', 'body', 'creation_date')
            VALUES (?, ?, ?);''',
            (request, body, creation_date))


def get_request(request, boundary_date):
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        data = cur.execute('''SELECT body FROM request_history
            WHERE request=? and creation_date>?;''',
            (request, boundary_date)).fetchall()
    return data[0][0] if len(data) else None