import sys
import os
import asyncio
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client_project'))

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          filters, ContextTypes, ConversationHandler, CallbackQueryHandler)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'client_project', '.env'))

from database import get_connection
from models import Client
from services import (find_client, send_email, save_client, get_all_clients,
                      get_databases_list, load_database_from_excel, delete_database)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_PASSWORD = os.getenv('BOT_PASSWORD')

(PASSWORD, SEARCH, DELETE_ID, EMAIL_SUBJECT, EMAIL_MESSAGE, EMAIL_DB,
 ADD_NAME, ADD_NUMBER, ADD_EMAIL,
 UPLOAD_DB_NAME, UPLOAD_FILE,
 DELETE_DB_NAME) = range(12)

MENU_KEYBOARD = [
    ['📋 Список клиентов', '➕ Добавить клиента'],
    ['🔍 Найти клиента', '🗑 Удалить клиента'],
    ['📧 Сделать рассылку', '📥 Загрузить базу'],
    ['🗂 Список баз', '❌ Удалить базу']
]

def format_client(p):
    return f"ID: {p[0]}\nИмя: {p[1]}\nНомер: {p[2]}\nПочта: {p[3]}\n\n"

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

async def check_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
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
    name = update.message.text.strip()
    if not name.replace(' ', '').isalpha():
        await update.message.reply_text('Имя должно содержать только буквы. Попробуй ещё раз:')
        return ADD_NAME
    context.user_data['name'] = name
    await update.message.reply_text('Введите номер клиента (11 цифр):')
    return ADD_NUMBER

async def add_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    if not number.isdigit() or len(number) != 11:
        await update.message.reply_text('Номер должен содержать 11 цифр. Попробуй ещё раз:')
        return ADD_NUMBER
    context.user_data['number'] = number
    await update.message.reply_text('Введите email клиента:')
    return ADD_EMAIL

async def add_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    if not re.match(pattern, email):
        await update.message.reply_text('Введите корректный email (например user@mail.ru):')
        return ADD_EMAIL
    client = Client(context.user_data['name'], context.user_data['number'], email)
    save_client(client)
    await update.message.reply_text(
        f"✅ Клиент добавлен!\n\n"
        f"Имя: {context.user_data['name']}\n"
        f"Номер: {context.user_data['number']}\n"
        f"Email: {email}"
    )
    context.user_data.pop('name', None)
    context.user_data.pop('number', None)
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
    await update.message.reply_text('Введите ID клиента для удаления:')
    return DELETE_ID

async def delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client_id = update.message.text.strip()
    if not client_id.isdigit():
        await update.message.reply_text('Введите корректный ID:')
        return DELETE_ID
    clients = get_all_clients()
    client = next((c for c in clients if str(c[0]) == client_id), None)
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
        context.user_data.pop('client_to_delete', None)
    else:
        await query.edit_message_text('Удаление отменено')

# ── Рассылка ───────────────────────────────────────────────────────────────

async def email_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return ConversationHandler.END
    databases = get_databases_list()
    if databases:
        text = 'Выберите базу для рассылки:\n\n'
        for db_id, db_name, total in databases:
            text += f"[{db_id}] {db_name} — {total} контактов\n"
        text += '\n[0] Вся база'
        await update.message.reply_text(text)
        return EMAIL_DB
    else:
        context.user_data['email_db_id'] = None
        await update.message.reply_text(
            'Загруженных баз нет — рассылка по всей базе\n\nВведите тему письма:'
        )
        return EMAIL_SUBJECT

async def email_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    if not choice.isdigit():
        await update.message.reply_text('Введите корректный id базы или 0 для всей базы:')
        return EMAIL_DB
    context.user_data['email_db_id'] = None if choice == '0' else int(choice)
    await update.message.reply_text('Введите тему письма:')
    return EMAIL_SUBJECT

async def email_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subject = update.message.text.strip()
    if not subject:
        await update.message.reply_text('Тема не может быть пустой. Введите тему письма:')
        return EMAIL_SUBJECT
    context.user_data['subject'] = subject
    await update.message.reply_text('Введите текст письма:')
    return EMAIL_MESSAGE

async def email_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()
    if not message:
        await update.message.reply_text('Текст не может быть пустым. Введите текст письма:')
        return EMAIL_MESSAGE

    subject = context.user_data['subject']
    db_id = context.user_data.get('email_db_id')

    conn = get_connection()
    cur = conn.cursor()
    if db_id is not None:
        cur.execute('SELECT id, name, email FROM clients WHERE db_id = %s', (db_id,))
    else:
        cur.execute('SELECT id, name, email FROM clients')
    clients = cur.fetchall()
    cur.close()
    conn.close()

    if not clients:
        await update.message.reply_text('В выбранной базе нет клиентов')
        return ConversationHandler.END

    await update.message.reply_text(f'⏳ Начинаем рассылку для {len(clients)} клиентов...')

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
    context.user_data.pop('subject', None)
    context.user_data.pop('email_db_id', None)
    return ConversationHandler.END

# ── Загрузить базу ─────────────────────────────────────────────────────────

async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return ConversationHandler.END
    await update.message.reply_text('Введите название для этой базы:')
    return UPLOAD_DB_NAME

async def upload_db_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_name = update.message.text.strip()
    if not db_name:
        await update.message.reply_text('Название не может быть пустым. Введите название базы:')
        return UPLOAD_DB_NAME
    context.user_data['db_name'] = db_name
    await update.message.reply_text('Пришлите Excel файл (.xlsx):')
    return UPLOAD_FILE

async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text(
            '⚠️ Пришлите файл в формате .xlsx\n'
            'Или нажмите /start чтобы вернуться в меню'
        )
        return UPLOAD_FILE

    file_name = update.message.document.file_name
    if not file_name.endswith('.xlsx'):
        await update.message.reply_text('Файл должен быть в формате .xlsx')
        return UPLOAD_FILE

    db_name = context.user_data['db_name']
    file = await context.bot.get_file(update.message.document.file_id)
    file_path = f'/tmp/{file_name}'
    await file.download_to_drive(file_path)

    try:
        added, skipped = load_database_from_excel(file_path, db_name)
        if added == 0:
            await update.message.reply_text(
                f'⚠️ Ничего не добавлено!\n\n'
                f'Пропущено строк: {skipped}\n\n'
                f'Убедись что заголовки в файле называются:\n'
                f'name/имя, email/почта, number/номер'
            )
        else:
            await update.message.reply_text(
                f'✅ База "{db_name}" загружена!\n\n'
                f'Добавлено: {added}\n'
                f'Пропущено: {skipped}'
            )
    except Exception as e:
        await update.message.reply_text(f'❌ Ошибка при загрузке файла: {e}')

    context.user_data.pop('db_name', None)
    return ConversationHandler.END

# ── Список баз ─────────────────────────────────────────────────────────────

async def show_databases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return
    databases = get_databases_list()
    if not databases:
        await update.message.reply_text('Загруженных баз нет')
        return
    text = 'Загруженные базы:\n\n'
    for db_id, db_name, total in databases:
        text += f"[{db_id}] {db_name} — {total} контактов\n"
    await update.message.reply_text(text)

# ── Удалить базу ───────────────────────────────────────────────────────────

async def delete_db_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_auth(update, context):
        return ConversationHandler.END
    databases = get_databases_list()
    if not databases:
        await update.message.reply_text('Загруженных баз нет')
        return ConversationHandler.END
    text = 'Загруженные базы:\n\n'
    for db_id, db_name, total in databases:
        text += f"[{db_id}] {db_name} — {total} контактов\n"
    text += '\nВведите название базы для удаления:'
    await update.message.reply_text(text)
    return DELETE_DB_NAME

async def delete_db_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_name = update.message.text.strip()
    if not db_name:
        await update.message.reply_text('Название не может быть пустым:')
        return DELETE_DB_NAME
    context.user_data['db_to_delete'] = db_name
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton('✅ Да', callback_data='delete_db_yes'),
        InlineKeyboardButton('❌ Нет', callback_data='delete_db_no')
    ]])
    await update.message.reply_text(
        f"Удалить базу '{db_name}' со всеми контактами?",
        reply_markup=keyboard
    )
    return ConversationHandler.END

async def delete_db_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'delete_db_yes':
        db_name = context.user_data.get('db_to_delete')
        count = delete_database(db_name)
        if count:
            await query.edit_message_text(f"🗑 База '{db_name}' удалена, {count} контактов удалено")
        else:
            await query.edit_message_text(f"База '{db_name}' не найдена")
        context.user_data.pop('db_to_delete', None)
    else:
        await query.edit_message_text('Удаление отменено')

# ── Main ───────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()

    auth_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)]},
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
            EMAIL_DB: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_db)],
            EMAIL_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_subject)],
            EMAIL_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_message)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    upload_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(['📥 Загрузить базу']), upload_start)],
        states={
            UPLOAD_DB_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, upload_db_name)],
            UPLOAD_FILE: [MessageHandler(filters.ALL, upload_file)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    delete_db_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(['❌ Удалить базу']), delete_db_start)],
        states={DELETE_DB_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_db_confirm)]},
        fallbacks=[CommandHandler('start', start)]
    )

    app.add_handler(auth_handler)
    app.add_handler(MessageHandler(filters.Text(['📋 Список клиентов']), show_clients))
    app.add_handler(MessageHandler(filters.Text(['🗂 Список баз']), show_databases))
    app.add_handler(search_handler)
    app.add_handler(add_handler)
    app.add_handler(delete_handler)
    app.add_handler(email_handler)
    app.add_handler(upload_handler)
    app.add_handler(delete_db_handler)
    app.add_handler(CallbackQueryHandler(delete_callback, pattern='^delete_yes$|^delete_no$'))
    app.add_handler(CallbackQueryHandler(delete_db_callback, pattern='^delete_db_'))

    print('Бот запущен...')
    app.run_polling()

if __name__ == '__main__':
    main()