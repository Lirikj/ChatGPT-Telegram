import sqlite3

def init_db():
    conn = sqlite3.connect('chat_database.db')
    c = conn.cursor()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT,
        last_name TEXT
    )
    ''')
    

    c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        conversation_id INTEGER DEFAULT 1,
        content TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    ''')
    
    conn.commit()
    conn.close()


def add_user(user_id, username, first_name, last_name):
    try:
        conn = sqlite3.connect('chat_database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if c.fetchone() is None:
            c.execute("INSERT INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                    (user_id, username, first_name, last_name))
        else:
            c.execute("UPDATE users SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?",
                    (username, first_name, last_name, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при добавлении/обновлении пользователя: {e}")


def clear_database(user_id):
    try:
        conn = sqlite3.connect('chat_database.db')
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка при очистке сообщений пользователя: {e}")

