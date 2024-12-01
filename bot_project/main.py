import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Подключение к базе данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Объект бота
bot = Bot(token="7425587886:AAEsXbkYzccFw_yJWBQAmm0ta8BjNCI_Cn0")
# Диспетчер
dp = Dispatcher()

# Проверка email и пароля
def check_credentials(email, password):
    cursor.execute("SELECT * FROM fixers WHERE email=? AND password=?", (email, password))
    return cursor.fetchone() is not None

# Состояния для FSM
class AuthStates(StatesGroup):
    email = State()
    password = State()

class TicketStates(StatesGroup):
    select_ticket = State()
    delete_ticket_id = State()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать! Пожалуйста, авторизуйтесь.\nВведите email:")
    await state.set_state(AuthStates.email)

@dp.message(AuthStates.email)
async def get_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Введите пароль:")
    await state.set_state(AuthStates.password)

@dp.message(AuthStates.password)
async def get_password(message: types.Message, state: FSMContext):
    password = message.text
    data = await state.get_data()
    email = data.get("email")
    if check_credentials(email, password):
        await state.clear()
        await message.answer("Авторизация успешна! Выберите действие:", reply_markup=get_main_keyboard())
    else:
        await message.answer("Неверный email или пароль. Попробуйте снова.\nВведите email:")
        await state.set_state(AuthStates.email)

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Показать тикеты"))
    builder.add(KeyboardButton(text="Удалить тикет"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# Хэндлер на кнопку "Показать тикеты"
@dp.message(lambda message: message.text == "Показать тикеты")
async def show_tickets(message: types.Message, state: FSMContext):
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    if tickets:
        response = "Список тикетов:\n"
        for ticket in tickets:
            status_translation = {
                "Ожидание": "Ожидание",
                "Завершен": "Завершен",
                "В работе": "В работе",
                "Просрочен": "Просрочен"
            }
            status = status_translation.get(ticket[3], "Неизвестный статус")
            response += f"{ticket[0]}. {ticket[1]} [{status}]\n"
        await message.answer(response, reply_markup=get_select_ticket_keyboard(tickets))
        await state.set_state(TicketStates.select_ticket)
    else:
        await message.answer("Нет доступных тикетов.")

def get_select_ticket_keyboard(tickets):
    builder = InlineKeyboardBuilder()
    for ticket in tickets:
        builder.add(InlineKeyboardButton(text=str(ticket[0]), callback_data=f"select_ticket_{ticket[0]}"))
    builder.adjust(2)
    return builder.as_markup()

@dp.callback_query(lambda c: c.data.startswith("select_ticket_"))
async def select_ticket(callback_query: types.CallbackQuery, state: FSMContext):
    ticket_id = callback_query.data.split("_")[2]
    cursor.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,))
    ticket = cursor.fetchone()
    if ticket:
        status_translation = {
            "Ожидание": "Ожидание",
            "Завершен": "Завершен",
            "В работе": "В работе",
            "Просрочен": "Просрочен"
        }
        status = status_translation.get(ticket[3], "Неизвестный статус")
        response = f"ID: {ticket[0]}, Заголовок: {ticket[1]}, Статус: {status}\nОписание: {ticket[2]}"
        await callback_query.message.answer(response, reply_markup=get_status_keyboard(ticket[0]))
    else:
        await callback_query.message.answer("Тикет не найден.")

def get_status_keyboard(ticket_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Ожидание", callback_data=f"status_waiting_{ticket_id}"))
    builder.add(InlineKeyboardButton(text="Завершен", callback_data=f"status_completed_{ticket_id}"))
    builder.add(InlineKeyboardButton(text="В работе", callback_data=f"status_in_progress_{ticket_id}"))
    builder.add(InlineKeyboardButton(text="Просрочен", callback_data=f"status_overdue_{ticket_id}"))
    builder.adjust(2)
    return builder.as_markup()

@dp.callback_query(lambda c: c.data.startswith("status_"))
async def change_status(callback_query: types.CallbackQuery):
    status = callback_query.data.split("_")[1]
    ticket_id = callback_query.data.split("_")[2]
    try:
        cursor.execute("UPDATE tickets SET status=? WHERE id=?", (status, ticket_id))
        conn.commit()
        await callback_query.message.answer(f"Статус тикета {ticket_id} изменен на {status}.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при изменении статуса тикета: {e}")
        await callback_query.message.answer("Произошла ошибка при изменении статуса тикета. Пожалуйста, попробуйте снова.")

# Хэндлер на кнопку "Удалить тикет"
@dp.message(lambda message: message.text == "Удалить тикет")
async def delete_ticket(message: types.Message, state: FSMContext):
    await message.answer("Введите ID тикета для удаления:")
    await state.set_state(TicketStates.delete_ticket_id)

@dp.message(TicketStates.delete_ticket_id)
async def delete_ticket_id(message: types.Message, state: FSMContext):
    ticket_id = message.text
    try:
        cursor.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
        conn.commit()
        await state.clear()
        await message.answer("Тикет успешно удален!")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при удалении тикета: {e}")
        await message.answer("Произошла ошибка при удалении тикета. Пожалуйста, попробуйте снова.")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())