from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_cities():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Название_города FROM Города")  # Получаем названия городов из таблицы "Города"
    cities = cursor.fetchall()
    conn.close()
    return cities

@app.route('/')
def index():
    # Получение списка городов
    cities = get_cities()

    # Получение параметра запроса для фильтрации по городу
    selected_city = request.args.get('city')

    # Подключение к базе данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Формирование SQL-запроса для получения пользователей с фильтрацией по городу, если указан
    if selected_city:
        cursor.execute("SELECT * FROM Пользователи WHERE Город=?", (selected_city,))
    else:
        cursor.execute("SELECT * FROM Пользователи")

    users = cursor.fetchall()

    # Закрытие соединения с базой данных
    conn.close()

    return render_template('index.html', users=users, cities=cities, selected_city=selected_city)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Подключение к базе данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Удаление пользователя из базы данных
    cursor.execute("DELETE FROM Пользователи WHERE id=?", (user_id,))
    conn.commit()

    # Закрытие соединения с базой данных
    conn.close()

    # Перенаправление на главную страницу
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_user():
    if request.method == 'POST':
        last_name = request.form['last_name']  # Отримання введеного прізвища з форми
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Пользователи WHERE Фамилия=?", (last_name,))
        users = cursor.fetchall()
        conn.close()
        return render_template('search_results.html', users=users, last_name=last_name)
    else:
        return render_template('search.html')


@app.route('/add_user', methods=['POST'])
def add_user():
    # Получение данных о новом пользователе из формы
    last_name = request.form['last_name']
    login = request.form['login']
    password = request.form['password']
    email = request.form['email']
    city = request.form.get('city') or request.form['other_city']

    # Подключение к базе данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Генерация регистрационного номера
    cursor.execute("SELECT MAX(РН) FROM Пользователи")
    max_reg_number = cursor.fetchone()[0]
    reg_number = max_reg_number + 1 if max_reg_number else 1

    # Добавление нового пользователя в базу данных
    cursor.execute('''INSERT INTO Пользователи (Фамилия, Логин, Пароль, Почта, Город, РН)
                      VALUES (?, ?, ?, ?, ?, ?)''', (last_name, login, password, email, city, reg_number))
    conn.commit()

    # Закрытие соединения с базой данных
    conn.close()

    # Перенаправление на главную страницу
    return redirect(url_for('index'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'GET':
        # Получение данных о пользователе для редактирования
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Пользователи WHERE id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        # Получение списка городов
        cities = get_cities()

        return render_template('edit_user.html', user=user, cities=cities)
    elif request.method == 'POST':
        # Получение данных о пользователе из формы редактирования
        last_name = request.form['last_name']
        login = request.form['login']
        password = request.form['password']
        email = request.form['email']
        city = request.form.get('city') or request.form['other_city']
        reg_number = request.form['reg_number']  # Получение нового значения РН

        # Подключение к базе данных
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Обновление данных о пользователе в базе данных
        cursor.execute('''UPDATE Пользователи 
                          SET Фамилия=?, Логин=?, Пароль=?, Почта=?, Город=?, РН=?
                          WHERE id=?''', (last_name, login, password, email, city, reg_number, user_id))
        conn.commit()

        # Закрытие соединения с базой данных
        conn.close()

        # Перенаправление на главную страницу
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
#Свой порт нужно прописать 
""" if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) """