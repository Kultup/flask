import sqlite3

# Подключение к базе данных бота
conn = sqlite3.connect('bot_users.db')
cursor = conn.cursor()

# Создание таблицы для хранения пользователей с полем для соли
cursor.execute('''CREATE TABLE IF NOT EXISTS Пользователи (
                  ID INTEGER PRIMARY KEY,
                  Фамилия TEXT,
                  Пароль TEXT,
                  Соль TEXT)''')
conn.commit()

# Закрытие соединения с базой данных
conn.close()
