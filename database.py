import sqlite3
import os

def get_user_db_path(user_id):
    return f'schedule_user_{user_id}.db'

def initialize_user_database(user_id):
    db_path = get_user_db_path(user_id)
    if not os.path.exists(db_path):
        try:
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schedules (
                    id INTEGER PRIMARY KEY,
                    day TEXT UNIQUE,
                    schedule TEXT
                )
            ''')
            connection.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при инициализации базы данных для пользователя {user_id}: {e}")
        finally:
            if connection:
                connection.close()

def add_user(user_id, full_name, role):
    db_path = "users.db"
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                full_name TEXT,
                role TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO users (user_id, full_name, role) 
            VALUES (?, ?, ?) ON CONFLICT(user_id) DO NOTHING
        ''', (user_id, full_name, role))

        connection.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении пользователя {user_id}: {e}")
    finally:
        if connection:
            connection.close()

def check_user_exists(user_id):
    db_path = "users.db"
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Ошибка при проверке пользователя {user_id}: {e}")
    finally:
        if connection:
            connection.close()

def add_schedule(user_id, day, schedule):
    db_path = get_user_db_path(user_id)
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO schedules (day, schedule) 
            VALUES (?, ?) ON CONFLICT(day) DO UPDATE SET schedule=excluded.schedule
        ''', (day, schedule))

        connection.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении расписания для пользователя {user_id}: {e}")
    finally:
        if connection:
            connection.close()

def get_schedule_for_day(user_id, day):
    db_path = get_user_db_path(user_id)
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT schedule FROM schedules WHERE day=?", (day,))
        result = cursor.fetchone()

        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Ошибка при получении расписания для пользователя {user_id}: {e}")
    finally:
        if connection:
            connection.close()

def update_schedule(user_id, day, new_schedule):
    db_path = get_user_db_path(user_id)
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute('''UPDATE schedules SET schedule=? WHERE day=?''', (new_schedule, day))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении расписания для пользователя {user_id}: {e}")
    finally:
        if connection:
            connection.close()
