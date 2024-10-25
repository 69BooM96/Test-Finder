import sqlite3

# Подключаемся к базе данных (файл .db будет создан автоматически)
connection = sqlite3.connect('plugins/pomahach/my_database.db')

# Создаём курсор для выполнения SQL-запросов
cursor = connection.cursor()

# Создание таблицы
cursor.execute('''
CREATE TABLE IF NOT EXISTS passengers (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    age INT,
    sex VARCHAR(10),
    class INT,
    survived BOOLEAN
);
''')

# Вставка данных в таблицу
cursor.executemany('''
INSERT INTO passengers (id, name, age, sex, class, survived) VALUES (?, ?, ?, ?, ?, ?)
''', [
    (1, 'John Smith', 34, 'male', 1, 1),
    (2, 'Jane Doe', 28, 'female', 2, 0),
    (3, 'Robert Brown', 45, 'male', 3, 0),
    (4, 'Emily White', 22, 'female', 1, 1),
    (5, 'Michael Green', 54, 'male', 2, 0)
])

# Выборка всех пассажиров
cursor.execute('SELECT * FROM passengers')
passengers = cursor.fetchall()

# Печать данных
for passenger in passengers:
    print(passenger)

# Сохраняем изменения
connection.commit()

# Закрываем соединение
connection.close()
