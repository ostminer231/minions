from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Для использования сессий

def get_db_connection():
    conn = sqlite3.connect('helpdesk.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/index")
def index():
    user_id = session['id']
    ticketsArr = []
    conn = get_db_connection()
    tickets = conn.execute('SELECT tickets.title, tickets.description, tickets.fixer_id, tickets.user_id, tickets.status, tickets.priority, tickets.id, tickets.type_id, users.username, fixers.username AS fixername FROM tickets WHERE user_id = ? JOIN users ON users.id = tickets.user_id JOIN fixers ON fixers.id = tickets.fixer_id', (user_id)).fetchall()
    for tick in tickets:
        ticketsArr.append(tick)
    conn.close()
    context = {
        "tickets": ticketsArr
    }
    return render_template("index.html", context=context)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Обработка данных формы
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['email'] = user['email']
            session['role'] = user['role_id']
            session['id'] = user['id']
            if user['role_id'] == 5:
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("index"))
        else:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM fixers WHERE email = ? AND password = ?', (username, password)).fetchone()
            conn.close()

            if user:
                session['email'] = user['email']
                session['role'] = user['role_id']
                if user['role_id'] == 5:
                    return redirect(url_for("admin"))
                else:
                    return redirect(url_for("tech"))
            else:
                flash("Неверный логин или пароль", "error")
                return render_template("login.html")
        
    
    return render_template("login.html")

# @app.route("/index")
# def index():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     conn = get_db_connection()
#     tickets = conn.execute('SELECT * FROM tickets').fetchall()
#     conn.close()
#     return render_template("index.html", tickets=tickets)

# @app.route("/", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
#         conn.close()

#         if user:
#             session['username'] = user['username']
#             session['role'] = user['role']
#             if user['role'] == 'admin':
#                 return redirect(url_for("admin"))
#             else:
#                 return redirect(url_for("index"))
#         else:
#             flash("Неверный логин или пароль", "error")
#             return render_template("autorization.html")

#     return render_template("autorization.html")

@app.route("/create", methods=["GET", "POST"])
def create_ticket():
    if request.method == "POST":
        # Обработка создания новой заявки
        new_ticket = {
            "id": len(tickets) + 1,
            "title": request.form["title"],
            "user": "Новый пользователь",
            "status": "Новая",
            "priority": "Низкий",
            "date": "2024-12-01"
        }
        tickets.append(new_ticket)
        return redirect(url_for("index"))
    return render_template("create.html")

@app.route("/admin")
def admin():
    # SELECT orders.created_at, orders.items_count, products.name
# FROM orders
# JOIN products ON products.id = orders.product_id;
    ticketsArr = []
    usersArr = []
    conn = get_db_connection()
    tickets = conn.execute('SELECT tickets.title, tickets.description, tickets.fixer_id, tickets.user_id, tickets.status, tickets.priority, tickets.id, tickets.type_id, users.username, fixers.username AS fixername FROM tickets JOIN users ON users.id = tickets.user_id JOIN fixers ON fixers.id = tickets.fixer_id').fetchall()
    for tick in tickets:
        ticketsArr.append(tick)
    users = conn.execute('SELECT users.username, users.id, users.email, users.priority, specializes.title FROM users JOIN specializes ON specializes.id = specialize_id').fetchall()
    for user in users:
        usersArr.append(user)
    conn.close()
    context = {
        "tickets": ticketsArr, "users": usersArr
    }
    return render_template("admin.html", context=context)

# @app.route("/update_ticket")
# def update_ticket():
#     conn = get_db_connection()
    
#     conn.execute('''
#             UPDATE tickets 
#             SET title = ?, 
#                 description = ?,
#                 status = ?,
#                 updated_at = DATETIME('now')
#             WHERE id = ?
#         ''', (
#             body.title,
#             data['description'],
#             data['status'],
#             id
#         ))
#     conn.close()

@app.route("/tech")
def tech():
    return render_template("tech.html")

@app.route("/ticket/<int:ticket_id>")
def view_ticket(ticket_id):
    # Поиск заявки по ID
    ticket = next((t for t in tickets if t["id"] == ticket_id), None)
    if not ticket:
        return "Заявка не найдена", 404
    return render_template("view_ticket.html", ticket=ticket, ticket_id=ticket_id)

if __name__ == "__main__":
    app.run(debug=True)