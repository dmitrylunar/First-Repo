import datetime, psycopg2, time

conn = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='qds123pprt',
    database='clients_db'
)
cur = conn.cursor()

class Client:
    def __init__(self, name, number, email):
        """Создание клиента с параметрами"""
        self.name = name
        self.number = number
        self.email = email

    def show_info(self):
        """Вывод информации о клиенте"""
        print (self.name)
        print (self.number)
        print (self.email)

    def to_dict(self):
        """Возврат списка параметров клиента"""
        return {'name': self.name, 'number': self.number, 'email': self.email}

def consolidate(func):
    def wrapper(*args, **kwargs):
        print ("Выполнить операцию? Y/N :")
        par = user_input()
        if par.lower() == "y":
            return func(*args, **kwargs)
        if par.lower() == "n":
            print ("Операция отменена...")
            return None
        else:
            print("Вы ввели что-то не так...")
            return None
    return wrapper

def user_input():
    """Пользовательский ввод"""
    user_in = input("Ввод: ")
    return user_in

def valid_name(name):
    """Валидация Имени"""
    while name == "" or not name.isalpha():
        name = input("Имя клиента должно содержать только буквы!\nВведите имя: ")
    else:
        return name

def valid_number(number):
    """Валидация номера телефона"""
    while number == "" or not number.isdigit() or len(number) != 11:
        number = input('Введите корректный номер из 11 цифр!\nВедите номер: ')
    else:
        return number

def valid_email(email):
    """Валидация Email"""
    while email == "":
        email = input('Введите email: ')
    else :
        return email

def valid_id(id):
    while id == "" or not id.isdigit():
        id = input('Введите корректный id: ')
    else:
        return id

def add_client():
        """Создание клиента с введенными данными и возврат объекта new_client"""
        print ("Дата записи: ", datetime.date.today())
        print("Введите данные о клиенте...")
        print ("Имя клиента: ")
        client_name = valid_name(user_input())
        print("Номер клиента: ")
        client_number = valid_number(user_input())
        print("Емейл клиента: ")
        client_email = valid_email(user_input())
        adding_client = Client(client_name, client_number, client_email)
        ready_client = adding_client.to_dict()
        print(ready_client)
        return Client(client_name, client_number, client_email)


def save_client(Client):
    """Создание и запись клиента с данными от пользователя"""
    cur.execute('INSERT INTO clients (name, number, email) VALUES (%s, %s, %s)', (Client.name, Client.number, Client.email))
    conn.commit()
    print("Клиент сохранен!")

@consolidate
def delete_client(choose):
    cur.execute('DELETE FROM clients WHERE id = %s', (choose,))
    conn.commit()
    print("Клиент удален...")

def delete_finding_client():
    client_list()
    print ('Выберете ID клиента которого хотите удалить..')
    choose = valid_id(user_input())
    cur.execute('SELECT * FROM clients WHERE id = %s', (choose,))
    client_to_delete = cur.fetchone()
    if client_to_delete is None:
        print("Клиент не обнаружен")
    else:
        print(f"ID: {client_to_delete[0]} \nИмя: {client_to_delete[1]}\nНомер: {client_to_delete[2]}\nПочта: {client_to_delete[3]}\n")
        delete_client(choose)


def client_list():
    """Вывод списка клиентов"""
    cur.execute('SELECT * FROM clients')
    clients = cur.fetchall()
    for person in clients:
        print(f"ID: {person[0]} \nИмя: {person[1]}\nНомер: {person[2]}\nПочта: {person[3]}\n")


def search_input():
    """Введение параметра для поиска"""
    print('Введите данные для поиска: ')
    search_info = user_input()
    return search_info

def find_client(search_info):
    """Поиск клиента по параметру(работает по всем полям)"""
    cur.execute("""SELECT * FROM clients
                   WHERE CAST(id AS text) LIKE %s 
                      OR name LIKE %s
                      OR number LIKE %s
                      OR email LIKE %s
                """,(f"%{search_info}%",) * 4)
    found = cur.fetchall()
    return found

def show_finding_client(found):
    """Отображение найденных клиентов с помощью поиска"""
    if found :
        for person in found:
            print(f"ID: {person[0]} \nИмя: {person[1]}\nНомер: {person[2]}\nПочта: {person[3]}\n")
    else :
        print('Совпадений не найдено')

def menu():
    """Вызов меню
    1 - Создание и запись клиента
    2 - Вывод списка клиентов
    3 - Поиск клиента
    4 - удаление клиента по номеру
    0 - Выход из программы"""
    while True:
        print ("\n""Выберете операцию: "
            "\nЧтобы добавить клиента в базу, введите 1"
            "\nЧтобы посмотреть всю базу клиентов, введите 2"
            "\nЧтобы найти клиента, введите 3"
            "\nЧтобы удалить клиента из списка, введите 4"
            "\nЧтобы закрыть программу, введите 0")
        choose = user_input()
        if choose == "1":
            save_client(add_client())
        elif choose == "2":
            client_list()
        elif choose == "3":
            show_finding_client(find_client(search_input()))
        elif choose == "4":
            delete_finding_client()
        elif choose == "0":
            print('Завершение программы...')
            cur.close()
            conn.close()
            break
        else:
            print("Вы ввели что-то не так")
        time.sleep(1.5)

menu()