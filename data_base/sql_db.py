import sqlite3 as sq


class Database:
    def __init__(self, db_name):
        self.conn = sq.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, text TEXT, done INTEGER)')

    def add_task(self, title, text):
        with self.conn:
            self.conn.execute(
                'INSERT INTO tasks (title, text, done) VALUES (?, ?, ?)',
                (title, text, 0))

    def mark_task_done(self, task_id):
        with self.conn:
            cursor = self.conn.execute(
                'UPDATE tasks SET done=1 WHERE id=?',
                (task_id,))
            return cursor.rowcount > 0

    def get_all_tasks(self):
        with self.conn:
            cursor = self.conn.execute(
                'SELECT id, title, text, done FROM tasks'
                )
            return [{'id': row[0],
                     'title': row[1],
                     'text': row[2],
                     'done': bool(row[3])} for row in cursor.fetchall()]

    def delete_task(self, task_id):
        with self.conn:
            cursor = self.conn.execute('DELETE FROM tasks WHERE id=?',
                                       (task_id,))
            return cursor.rowcount > 0
