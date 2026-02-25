import datetime, json

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

def user_input():
    user_in = input("Ввод: ")
    return user_in

def valid_name(name):
    while name == "" or not name.isalpha():
        name = input("Имя клиента должно содержать только буквы!\nВведите имя: ")
    else:
        return name

def valid_number(number):
    while number == "" or not number.isdigit() or len(number) != 11:
        number = input('Введите корректный номер из 11 цифр!\nВедите номер: ')
    else:
        return number

def valid_email(email):
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

def client_list():
    with open("clients.json", "r") as file:
        response = json.load(file)
        for client in response:
            print('\nИмя: ', client["name"], '\nДата: ', client["date"], '\nВозраст: ', client["age"], '\nНомер: ',
                  client["num"])


def find_client_with_num():
    find = input("Введите данные для поиска: ")
    while find == "":
        find = input("Введите корректный запрос: ")
    with open("../../clients.json", "r") as file:
        response = json.load(file)
        found = False
        for client in response:
            if find == client["num"] or find == client["name"] or find == client["date"] or find == client["age"]:
                print('Имя: ', client["name"], '\nДата: ', client["date"], '\nВозраст: ', client["age"], '\nНомер: ',
                      client["num"])
                found = True
                break
        if not found:
            print('Клиент не обнаружен!')

def check_data():
    try:
        file = open("../../clients.json", "r")
        json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        file = open("../../clients.json", "w")
        file.write("[]")

def menu():
    """Вызов меню
    1 - Создание и запись клиента
    2 - Выведение списка клиентов
    3 - Поиск клиента по номеру
    0 - Выход из программы"""

    print ("Выберете операцию: \nЧтобы добавить клиента в базу, введите 1"
        "\nЧтобы посмотреть всю базу клиентов, введите 2"
        "\nЧтобы найти данные клиента по номеру телефона, введите 3"
        "\nЧтобы закрыть программу, введите 0")
    choose = input("Выберете пункт меню : ")
    if choose == "1":
        save_client(add_client())
    elif choose == "2":
        client_list()
    elif choose == "3":
        find_client_with_num()
    elif choose == "0":
        pass
    else:
        print("Вы ввели что-то не так")

add_client()