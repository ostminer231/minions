import sqlite3
def populate_db():
    conn = sqlite3.connect('helpdesk.db')
    cursor = conn.cursor()

    tickets = [
        ('Ремонт принтера', 'Принтер сломался, помогите', 'Низкий', "2024-11-11", '2024-11-25', 2, 2, 1),
        ('Клавиатура сломалась', 'Кнопки выпали', 'Низкий', "2024-11-10", '2024-11-24', 1, 2, 1)
    ]
    cursor.executemany('INSERT OR IGNORE INTO tickets (title, description, priority, date, end_date, user_id, fixer_id, type_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', tickets)

    conn.commit()
    conn.close()

name = "main"

if name == 'main':
    populate_db()