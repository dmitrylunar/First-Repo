import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client_project'))

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          filters, ContextTypes, ConversationHandler, CallbackQueryHandler)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'client_project', '.env'))

from services import find_client, send_bulk_email
from database import get_connection

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_PASSWORD = os.getenv('BOT_PASSWORD')

PASSWORD, SEARCH, DELETE_ID, EMAIL_SUBJECT, EMAIL_MESSAGE, ADD_NAME, ADD_NUMBER, ADD_EMAIL = range(8)

MENU_KEYBOARD = [
    ['📋 Список клиентов', '➕ Добавить клиента'],
    ['🔍 Найти клиента', '🗑 Удалить клиента'],
    ['📧 Сделать рассылку']
]

def format_client(p):
    return f"ID: {p[0]}\nИмя: {p[1]}\nНомер: {p[2]}\nПочта: {p[3]}\n\n"

def get_all_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients')
    clients = cur.fetchall()
    cur.close()
    conn.close()
    return clients

def is_authorized(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.user_data.get('authorized', False)

# ── Авторизация ────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_authorized(context):
        await update.message.reply_text(
            'Привет! Я бот для управления клиентской базой.',
            reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, resize_keyboard=True)
        )
        return ConversationHandler.END
    await update.message.reply_text('Введите пароль доступа:')
    return PASSWORD

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == BOT_PASSWORD:
        context.user_data['authorized'] = True
        await update.message.reply_text(
            '✅ Доступ разрешён!',
            reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, resize_keyboard=True)
        )
    else:
        await update.message.reply_text('❌ Неверный пароль. Попробуй ещё раз:')
        return PASSWORD
    return ConversationHandler.END

async def check_auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка авторизации перед любым действием"""
    if not is_authorized(context):
        await update.message.reply_text('Введите /start и войдите с паролем')
        return False
    return True

# ── Список клиентов ────────────────────────────────────────────────────────

async def show_clients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return
    clients = get_all_clients()
    if not clients:
        await update.message.reply_text('База клиентов пуста')
        return
    text = ''.join(format_client(p) for p in clients)
    await update.message.reply_text(text)

# ── Поиск ──────────────────────────────────────────────────────────────────

async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return ConversationHandler.END
    await update.message.reply_text('Введите данные для поиска:')
    return SEARCH

async def search_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = find_client(update.message.text)
    if results:
        text = ''.join(format_client(p) for p in results)
    else:
        text = 'Совпадений не найдено'
    await update.message.reply_text(text)
    return ConversationHandler.END

# ── Добавить клиента ───────────────────────────────────────────────────────

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return ConversationHandler.END
    await update.message.reply_text('Введите имя клиента:')
    return ADD_NAME

async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if not name.isalpha():
        await update.message.reply_text('Имя должно содержать только буквы. Попробуй ещё раз:')
        return ADD_NAME
    context.user_data['name'] = name
    await update.message.reply_text('Введите номер клиента (11 цифр начиная с 8):')
    return ADD_NUMBER

async def add_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text
    if not number.isdigit() or len(number) != 11:
        await update.message.reply_text('Номер должен содержать 11 цифр. Попробуй ещё раз:')
        return ADD_NUMBER
    context.user_data['number'] = number
    await update.message.reply_text('Введите email клиента:')
    return ADD_EMAIL

async def add_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO clients (name, number, email) VALUES (%s, %s, %s)',
                (context.user_data['name'], context.user_data['number'], email))
    conn.commit()
    cur.close()
    conn.close()
    await update.message.reply_text(
        f"✅ Клиент добавлен!\n\n"
        f"Имя: {context.user_data['name']}\n"
        f"Номер: {context.user_data['number']}\n"
        f"Email: {email}"
    )
    context.user_data['authorized'] = True
    context.user_data.pop('name', None)
    context.user_data.pop('number', None)
    context.user_data.pop('email', None)
    return ConversationHandler.END

# ── Удалить клиента ────────────────────────────────────────────────────────

async def delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return ConversationHandler.END
    clients = get_all_clients()
    if not clients:
        await update.message.reply_text('База клиентов пуста')
        return ConversationHandler.END
    text = ''.join(format_client(p) for p in clients)
    await update.message.reply_text(text)
    await update.message.reply_text('Введите ID клиента которого хотите удалить:')
    return DELETE_ID

async def delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client_id = update.message.text
    if not client_id.isdigit():
        await update.message.reply_text('Введите корректный ID:')
        return DELETE_ID
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients WHERE id = %s', (client_id,))
    client = cur.fetchone()
    cur.close()
    conn.close()
    if client is None:
        await update.message.reply_text('Клиент не найден')
        return ConversationHandler.END
    context.user_data['client_to_delete'] = client
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton('✅ Да', callback_data='delete_yes'),
        InlineKeyboardButton('❌ Нет', callback_data='delete_no')
    ]])
    await update.message.reply_text(
        f"Удалить клиента?\n\nИмя: {client[1]}\nНомер: {client[2]}\nПочта: {client[3]}",
        reply_markup=keyboard
    )
    return ConversationHandler.END

async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'delete_yes':
        client = context.user_data.get('client_to_delete')
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM clients WHERE id = %s', (client[0],))
        conn.commit()
        cur.close()
        conn.close()
        await query.edit_message_text(f"🗑 Клиент {client[1]} удалён")
        context.user_data['authorized'] = True
        context.user_data.pop('client_to_delete', None)
    else:
        await query.edit_message_text('Удаление отменено')

# ── Рассылка ───────────────────────────────────────────────────────────────

async def email_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return ConversationHandler.END
    await update.message.reply_text('Введите тему письма:')
    return EMAIL_SUBJECT

async def email_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['subject'] = update.message.text
    await update.message.reply_text('Введите текст письма:')
    return EMAIL_MESSAGE

async def email_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subject = context.user_data['subject']
    message = update.message.text

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name, email FROM clients')
    clients = cur.fetchall()
    cur.close()
    conn.close()

    if not clients:
        await update.message.reply_text('База клиентов пуста')
        return ConversationHandler.END

    await update.message.reply_text(f'⏳ Начинаем рассылку для {len(clients)} клиентов...')

    from services import send_email
    success = 0
    failed = 0

    for client_id, name, email in clients:
        if email:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, send_email, email, name, subject, message)
            if result:
                success += 1
            else:
                failed += 1

    await update.message.reply_text(
        f"✅ Рассылка завершена!\n\n"
        f"Отправлено: {success}\n"
        f"Ошибок: {failed}"
    )
    context.user_data['authorized'] = True
    context.user_data.pop('subject', None)
    return ConversationHandler.END

# ── Main ───────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()

    auth_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)]
        },
        fallbacks=[]
    )

    search_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(['🔍 Найти клиента']), search_start)],
        states={SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_result)]},
        fallbacks=[CommandHandler('start', start)]
    )

    add_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(['➕ Добавить клиента']), add_start)],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_name)],
            ADD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_number)],
            ADD_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_email)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    delete_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(['🗑 Удалить клиента']), delete_start)],
        states={DELETE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_confirm)]},
        fallbacks=[CommandHandler('start', start)]
    )

    email_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(['📧 Сделать рассылку']), email_start)],
        states={
            EMAIL_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_subject)],
            EMAIL_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_message)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    app.add_handler(auth_handler)
    app.add_handler(MessageHandler(filters.Text(['📋 Список клиентов']), show_clients))
    app.add_handler(search_handler)
    app.add_handler(add_handler)
    app.add_handler(delete_handler)
    app.add_handler(email_handler)
    app.add_handler(CallbackQueryHandler(delete_callback, pattern='^delete_'))

    print('Бот запущен...')
    app.run_polling()

if __name__ == '__main__':
    main()