from database import get_connection
from models import Client
import datetime
from utils import consolidate
from validators import valid_name, valid_number, valid_email, valid_id
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
load_dotenv()

def add_client():
    print("Дата записи: ", datetime.date.today())
    print("Введите данные о клиенте...")
    name = valid_name(input("Имя клиента: "))
    number = valid_number(input("Номер клиента: "))
    email = valid_email(input("Емейл клиента: "))
    return Client(name, number, email)

def save_client(client):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO clients (name, number, email) VALUES (%s, %s, %s)',
                (client.name, client.number, client.email))
    conn.commit()
    cur.close()
    conn.close()
    print("Клиент сохранен!")

@consolidate
def delete_client(choose):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM clients WHERE id = %s', (choose,))
    conn.commit()
    cur.close()
    conn.close()
    print("Клиент удален...")

def client_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients')
    clients = cur.fetchall()
    cur.close()
    conn.close()
    for person in clients:
        print(f"ID: {person[0]} \nИмя: {person[1]}\nНомер: {person[2]}\nПочта: {person[3]}\n")

def find_client(search_info):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM clients
                   WHERE CAST(id AS text) LIKE %s
                      OR name LIKE %s
                      OR number LIKE %s
                      OR email LIKE %s
                """, (f"%{search_info}%",) * 4)
    found = cur.fetchall()
    cur.close()
    conn.close()
    return found

def delete_finding_client():
    client_list()
    print('Выберете ID клиента которого хотите удалить..')
    choose = valid_id(input("Ввод: "))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM clients WHERE id = %s', (choose,))
    client_to_delete = cur.fetchone()
    cur.close()
    conn.close()
    if client_to_delete is None:
        print("Клиент не обнаружен")
    else:
        print(f"ID: {client_to_delete[0]} \nИмя: {client_to_delete[1]}\nНомер: {client_to_delete[2]}\nПочта: {client_to_delete[3]}\n")
        delete_client(choose)
    
def build_email(from_email, to_email, to_name, subject, message):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    body = f"Привет, {to_name}!\n\n{message}"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    return msg

def send_email(to_email, to_name, subject, message):
    from_email = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_PASSWORD')

    msg = build_email(from_email, to_email, to_name, subject, message)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
        print(f"Отправлено: {to_name} <{to_email}>")
        return True
    except Exception as e:
        print(f"Ошибка для {to_email}: {e}")
        return False
    
def send_bulk_email(subject, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, name, email FROM clients')
    clients = cur.fetchall()
    cur.close()
    conn.close()

    if not clients:
        print("База клиентов пуста")
        return

    print(f"\nНачинаем рассылку для {len(clients)} клиентов...\n")

    success = 0
    failed = 0

    for client_id, name, email in clients:
        if email:
            result = send_email(email, name, subject, message)
            if result:
                success += 1
            else:
                failed += 1
        else:
            print(f"Нет email у клиента {name} (id={client_id})")

    print(f"\nГотово: {success} отправлено, {failed} ошибок")
