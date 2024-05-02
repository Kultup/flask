import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создание таблицы "Пользователи" с добавлением столбца "РН"
cursor.execute('''CREATE TABLE IF NOT EXISTS Пользователи (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Фамилия TEXT NOT NULL,
                    Логин TEXT NOT NULL,
                    Пароль TEXT NOT NULL,
                    Почта TEXT NOT NULL,
                    Город TEXT NOT NULL,
                    РН INTEGER UNIQUE NOT NULL
                )''')

# Функция для генерации регистрационного номера
def generate_registration_number(cursor):
    # Получаем максимальный регистрационный номер из базы данных
    cursor.execute("SELECT MAX(РН) FROM Пользователи")
    max_reg_number = cursor.fetchone()[0]

    # Если таблица пуста, начинаем с 1, иначе увеличиваем максимальный на 1
    return max_reg_number + 1 if max_reg_number else 1

# Создание таблицы "Города"
cursor.execute('''CREATE TABLE IF NOT EXISTS Города (
                    Город_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Название_города TEXT NOT NULL
                )''')

# Добавление данных в таблицу "Города"
cities = [
    ('Київ (Оболонь)',),
    ('Житомир',),
    ('Луцьк',),
    ('Львів',),
    ('Вінниця',),
    ('Київ (Позняки)',),
    ('Одеса (Котовського)',),
    ('Хмельницький',),
    ('Чернівці',),
    ('Тернопіль',),
    ('Одеса (Совіньйон)',)
]
cursor.executemany("INSERT INTO Города (Название_города) VALUES (?)", cities)

# Сохранение изменений
conn.commit()

# Проверка успешности добавления данных в таблицу "Города"
cursor.execute("SELECT COUNT(*) FROM Города")
count = cursor.fetchone()[0]
if count > 0:
    print("Данные успешно добавлены в таблицу 'Города'.")
else:
    print("Возникла ошибка при добавлении данных в таблицу 'Города'.")

# Закрытие соединения с базой данных
conn.close()
