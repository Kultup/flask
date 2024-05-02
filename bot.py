import sqlite3
import telebot
import json
import bcrypt
import secrets
import logging

# Настройка логирования
logging.basicConfig(filename='bot_errors.log', level=logging.WARNING)

# Загрузка конфигурации из файла
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    logging.error("Файл конфигурации не найден")
    raise

# Получение данных из конфигурации
bot_token = config.get('bot_token')

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Генерация случайной соли
def generate_salt():
    return bcrypt.gensalt().decode('utf-8')

# Функция для хеширования пароля с использованием соли
def hash_password(password, salt):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8'))
    return hashed_password.decode('utf-8')

# Функция для отправки текстового сообщения в чат Telegram
def type_text(chat_id, text):
    bot.send_message(chat_id, text)

# Функция для отправки текстового сообщения с анимацией в чат Telegram
def type_text_with_animation(chat_id, text, animation):
    bot.send_message(chat_id, text)
    bot.send_animation(chat_id, animation)
# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        # Подключение к базе данных бота
        with sqlite3.connect('bot_users.db') as conn_bot:
            cursor_bot = conn_bot.cursor()

            # Проверка, есть ли уже у пользователя фамилия в базе данных бота
            cursor_bot.execute("SELECT Фамилия FROM Пользователи WHERE ID=?", (message.chat.id,))
            result_bot = cursor_bot.fetchone()

            # Якщо фамілія вже є в базі даних бота, відправляємо повідомлення про успішну реєстрацію
            if result_bot and result_bot[0]:
                bot.send_message(message.chat.id, f"Ви вже зареєстровані, {result_bot[0]}!")
            else:
                # Відправляємо коротке описання можливостей бота
                bot.send_message(message.chat.id, "Привіт! Я бот, який допоможе вам отримати доступ до вашої хмарової платформи, поштового акаунту та навіть вашого комп'ютера. Просто надішліть своє ім'я та прізвище, щоб отримати логін та пароль.")
                # Отправляем сообщение с запросом фамилии
                bot.send_message(message.chat.id, "Введіть ваше Ім'я Прізвище:")

                # Ожидаем ответ пользователя с фамилией
                bot.register_next_step_handler(message, lambda msg: handle_lastname_input(msg, conn_bot))
    except sqlite3.Error as e:
        logging.error(f"Помилка SQLite: {e}")
        bot.send_message(message.chat.id, "Виникла помилка. Будь ласка, спробуйте пізніше.")


# Обработчик ввода фамилии
def handle_lastname_input(message, conn_bot):
    try:
        # Получаем введенную фамилию
        lastname = message.text

        # Вставляем фамилию пользователя в базу данных бота
        cursor_bot = conn_bot.cursor()
        cursor_bot.execute("INSERT INTO Пользователи (ID, Фамилия) VALUES (?, ?)", (message.chat.id, lastname))
        conn_bot.commit()

        # Генерируем соль и хэшируем пароль для пользователя
        password = generate_password()
        salt = generate_salt()
        hashed_password = hash_password(password, salt)
        cursor_bot.execute("UPDATE Пользователи SET Пароль=?, Соль=? WHERE ID=?", (hashed_password, salt, message.chat.id))
        conn_bot.commit()

        # Отправляем сообщение с паролем пользователю
        bot.send_message(message.chat.id, f"Ви успішно зареєстровані, {lastname}! Ваш пароль: {password}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite: {e}")
        bot.send_message(message.chat.id, "Виникла помилка. Будь ласка, спробуйте пізніше.")

# Функция для генерации пароля
def generate_password():
    return ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(8))


# Обработчик команды /info
@bot.message_handler(commands=['info'])
def handle_info(message):
    try:
        # Подключение к базе данных бота
        with sqlite3.connect('bot_users.db') as conn_bot:
            cursor_bot = conn_bot.cursor()

            # Проверяем, есть ли уже у пользователя фамилия в базе данных бота
            cursor_bot.execute("SELECT Фамилия, Пароль, Соль FROM Пользователи WHERE ID=?", (message.chat.id,))
            result_bot = cursor_bot.fetchone()

            # Если фамилия уже есть в базе данных бота, продолжаем выполнение команды /info
            if result_bot and result_bot[0]:
                # Отправляем сообщение с запросом фамилии для получения данных
                bot.send_message(message.chat.id, "Введіть Ваше Ім'я Прізвище для отримання даних:")
                
                # Ожидаем ответ пользователя с фамилией
                bot.register_next_step_handler(message, lambda msg: handle_info_lastname_input(msg, result_bot[0], result_bot[1], result_bot[2]))
            else:
                bot.send_message(message.chat.id, "Ви не зареєстровані. Будь ласка, скористайтеся командою /start для реєстрації.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite: {e}")
        bot.send_message(message.chat.id, "Виникла помилка. Будь ласка, спробуйте пізніше.")

# Обработчик ввода фамилии для получения информации
def handle_info_lastname_input(message, user_lastname, hashed_password, salt):
    try:
        # Получаем введенную фамилию
        requested_lastname = message.text

        # Проверяем, имеет ли пользователь право доступа к информации
        if requested_lastname == user_lastname:
            # Подключение к базе данных пользователей
            with sqlite3.connect('users.db') as conn_users:
                cursor_users = conn_users.cursor()

                # Получаем информацию о пользователе по фамилии из базы данных пользователей
                cursor_users.execute("SELECT * FROM Пользователи WHERE Фамилия=?", (requested_lastname,))
                result_users = cursor_users.fetchone()

                # Если информация найдена, отправляем её пользователю
                if result_users:
                    # Форматируем текст для красивого вывода
                    user_info = f"""Інформація про користувача:
Прізвище: {result_users[1]}
Логін: {result_users[2]}
Пароль: {result_users[3]}
Email: {result_users[4]}
Місто: {result_users[5]}
"""
                    bot.send_message(message.chat.id, user_info)
                else:
                    bot.send_message(message.chat.id, f"Користувача з прізвищем'{requested_lastname}' не знадено.")
        else:
            logging.warning(f"Пользователь {message.chat.id} попытался получить доступ к информации с другой фамилией: {requested_lastname}")
            bot.send_message(message.chat.id, "У вас немає доступу до інформації про цього користувача.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite: {e}")
        bot.send_message(message.chat.id, "Виникла помилка. Будь ласка, спробуйте пізніше.")

# Запуск бота
try:
    bot.polling()
except Exception as e:
    logging.error(f"Ошибка при запуске бота: {e}")
