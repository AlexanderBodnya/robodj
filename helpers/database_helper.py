import sqlite3

def connect(database):
    db = sqlite3.connect(database)
    cur = db.cursor()
    init_db(cur)
    db.commit()
    return cur, db

def init_db(cur):
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS users (user_id INTEGER,
                                             chat_id INTEGER,
                                             pair_id INTEGER,
                                             name TEXT,
                                             nickname TEXT,
                                             pair_name TEXT,
                                             PRIMARY KEY(user_id))''')

    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS `IX_uid` ON `users` ( `user_id` )")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS `IX_cid` ON `users` ( `chat_id` )")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS `IX_pid` ON `users` ( `pair_id` )")

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS history (from_user_id INTEGER,
                                               to_user_id INTEGER,
                                               pair_id INTEGER,
                                               message TEXT,
                                               from_nickname TEXT,
                                               to_nickname TEXT,
                                               created_at TIMESTAMP,
                                               FOREIGN KEY (from_user_id) REFERENCES users(user_id),
                                               FOREIGN KEY (to_user_id) REFERENCES users(user_id),
                                               FOREIGN KEY (pair_id) REFERENCES users(pair_id))''')
    cur.execute("CREATE INDEX IF NOT EXISTS `IX_fuid` ON `history` ( `from_user_id` )")
    cur.execute("CREATE INDEX IF NOT EXISTS `IX_tuid` ON `history` ( `to_user_id` )")
    cur.execute("CREATE INDEX IF NOT EXISTS `IX_pid` ON `history` ( `pair_id` )")


def store_message(cur, from_user_id, from_nickname, message):
    cur.execute('INSERT INTO history (from_user_id, from_nickname, message) VALUES(?,?,?)',(from_user_id, from_nickname, message))

def add_user(cur, user_id, chat_id, nickname):
    cur.execute('INSERT OR IGNORE INTO users (user_id, chat_id, nickname) VALUES(?,?,?)',(user_id, chat_id, nickname))
