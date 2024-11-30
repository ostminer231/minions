import sqlite3

def create_db():
    conn = sqlite3.connect('helpdesk.db')
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER,
	"username"	TEXT,
	"email"	TEXT UNIQUE,
	"priority"	TEXT,
	"specialize_id"	INTEGER,
	"role_id"	INTEGER DEFAULT 1,
	"password"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("specialize_id") REFERENCES "specializes"("id")
    )
    ''')

    # Создание таблицы заявок
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "tickets" (
	"id"	INTEGER,
	"title"	TEXT NOT NULL,
	"description"	TEXT DEFAULT 'Без описания',
	"status"	TEXT NOT NULL DEFAULT 'Ожидание',
	"priority"	TEXT,
	"date"	TEXT,
	"end_date"	TEXT,
	"user_id"	INTEGER,
	"fixer_id"	INTEGER,
	"type_id"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "users"("id"),
	FOREIGN KEY("fixer_id") REFERENCES "fixers"("id")
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "roles" (
	"id"	INTEGER,
	"title"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "fixers" (
	"id"	INTEGER,
	"username"	TEXT,
	"email"	TEXT UNIQUE,
	"priority"	TEXT,
	"specialize_id"	INTEGER,
	"role_id"	INTEGER DEFAULT 2,
	"password"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("specialize_id") REFERENCES "specializeIds"("id")
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "specializes" (
	"id"	INTEGER,
	"title"	TEXT,
	"priority"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "types" (
	"id"	INTEGER,
	"title"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
    )
    ''')

    # Добавление тестовых данных
    users = [
        ('Иванов И.И.', 'test@mail.ru', 'Средний', 1, 1, '111'),
        ('Илькаев Н.Р.', 'admin@mail.ru', 'Высокий', 5, 5, '444')
    ]
    cursor.executemany('INSERT OR IGNORE INTO users (username, email, priority, specialize_id, role_id, password) VALUES (?, ?, ?, ?, ?, ?)', users)
    fixers = [
        ('Сидорова А.В.', 'test1@mail.ru', 'Средний', 4, 2, '222'),
        ('Кузахметова А.Н.', 'test2@mail.ru', 'Средний', 4, 3, '333')
    ]
    cursor.executemany('INSERT OR IGNORE INTO fixers (username, email, priority, specialize_id, role_id, password) VALUES (?, ?, ?, ?, ?, ?)', fixers)
    tickets = [
        ('Ремонт ноутбука', 'Почините мне ноут', 'Средний', "2024-12-01", '2024-12-15', 1, 1, 1)
    ]
    cursor.executemany('INSERT OR IGNORE INTO tickets (title, description, priority, date, end_date, user_id, fixer_id, type_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', tickets)
    roles = [
        ('Пользователь',),
        ('Техник-ремонт',),
        ('Техник-обслуживание',),
        ('Техник-установка',),
        ('Админ',)
    ]
    cursor.executemany('INSERT OR IGNORE INTO roles (title) VALUES (?)', roles)
    specializes = [
        ('Бухгалтер', 'Средний',),
        ('Экономист', 'Низкий',),
        ('Генеральный директор', 'Высокий',),
        ('Инженер-электроник', 'Средний',),
        ('Администратор', 'Высокий',)
    ]
    cursor.executemany('INSERT OR IGNORE INTO specializes (title, priority) VALUES (?, ?)', specializes)
    types = [
        ('Ремонт',),
        ('Обслуживание',),
        ('Установка',)
    ]
    cursor.executemany('INSERT OR IGNORE INTO types (title) VALUES (?)', types)

    conn.commit()
    conn.close()

name = "main"

if name == 'main':
    create_db()