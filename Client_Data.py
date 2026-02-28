import datetime, json, re
import time


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
        return ready_client


def save_client(saving_client):
    """Создание и запись клиента с данными от пользователя"""
    with open("clients.json", "r") as file:
        data = json.load(file)
        data.append(saving_client)
    with open("clients.json", "w") as file:
        json.dump(data, file, indent=4)
    print("Клиент сохранен!")

@consolidate
def delete_client(client):
    with open("clients.json", "r") as file:
        data = json.load(file)
        data.remove(client.to_dict())
    with open("clients.json", "w") as file:
        json.dump(data, file, indent=4)
        print("Клиент удален...")

def delete_finding_client():
    client_list()
    print ('Введите номер клиента, которого хотите удалить...')
    choose = valid_number(user_input())
    client_to_delete = None
    with open("clients.json", "r") as file:
        response = json.load(file)
        for client in response:
            if choose == str(client["number"]):
                client_to_delete = Client(**client)
                print(client_to_delete.to_dict())
                break

    if client_to_delete is None:
        print("Клиент не обнаружен")
    else:
        delete_client(client_to_delete)






def client_list():
    """Вывод списка клиентов"""
    with open("clients.json", "r") as file:
        response = json.load(file)
        for client in response:
            print('\nИмя: ', client["name"], '\nНомер телефона: ', client["number"], '\nEmail: ',
                  client["email"])

def search_input():
    """Введение параметра для поиска"""
    print('Введите данные для поиска: ')
    search_info = user_input()
    return search_info

def find_client(search_info):
    """Поиск клиента по параметру(работает по всем полям)"""
    with open("clients.json", "r") as file:
        response = json.load(file)
        found = []
        for client in response:
            client_obj = Client(**client)
            if re.search(re.escape(search_info), str(client_obj.to_dict()), re.I):
                    found.append(client_obj)
    return found

def show_finding_client(found):
    """Отображение найденных клиентов с помощью поиска"""
    if found :
        for client in found:
            print('Имя клиента: ', client.name,'\n''Номер клиента: ',client.number,'\n''Емейл клиента: ', client.email, '\n')
    else :
        print('Совпадений не найдено')

def check_data():
    """Проверка наличия файла json"""
    try:
        with open("clients.json", "r") as file:
            json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        with open("clients.json", "w") as file:
            file.write("[]")

def menu():
    """Вызов меню
    1 - Создание и запись клиента
    2 - Вывод списка клиентов
    3 - Поиск клиента
    4 - удаление клиента по номеру
    0 - Выход из программы"""
    check_data()
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
            break
        else:
            print("Вы ввели что-то не так")
        time.sleep(1.5)

menu()