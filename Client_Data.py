import datetime, json, psycopg2
"""Подключение библиотек """
"""Check git"""
class Client:
    def __init__(self, date, name, age, num):
        """Создание клиента с параметрами"""
        self.date = date
        self.name = name
        self.age = age
        self.num = num
        print  ("\nЗапись создана!\n")
    def show_info(self):
        """Вывод информации о клиенте"""
        print (self.date)
        print (self.name)
        print (self.age)
        print (self.num)
    def to_dict(self):
        """Возврат списка параметров клиента"""
        return {'date': self.date, 'name': self.name, 'age': self.age, 'num': self.num}

def add_client():
        """Создание клиента с введенными данными и возврат объекта new_client"""
        print ("Дата записи: ", datetime.date.today())
        client_date = datetime.date.today()
        client_date = client_date.strftime("%Y-%m-%d")
        print("Введите данные о клиенте...")
        client_name = input("Имя клиента: ")
        while client_name == "" or not client_name.isalpha():
            client_name = input("Имя клиента должно содержать только буквы и содержать хотя бы один символ!\nВведите имя: ")
        client_age = input("Возраст клиента: ")
        while client_age == "" or not client_age.isdigit() or int(client_age) <= 0 or int(client_age) >= 100:
            client_age = input("Возраст не может быть меньше 0 или больше 99, а так же содержать только буквы!\nВозраст клиента: ")
        client_num = input("Номер клиента: ")
        while client_num == "" or not client_num.isdigit() or len(client_num) != 11:
            client_num = input("Введите коректный номер из 11 цифр!\nВведите номер: ")
        new_client = Client(client_date, client_name, client_age, client_num)
        return new_client

def save_client():
    """Создание и запись клиента с данными от пользователя"""
    saving_client = add_client().to_dict()
    with open("../../clients.json", "r") as file:
        data = json.load(file)
        data.append(saving_client)
    with open("../../clients.json", "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print("Клиент сохранен!")

def client_list():
    with open("../../clients.json", "r") as file:
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
        save_client()
    elif choose == "2":
        client_list()
    elif choose == "3":
        find_client_with_num()
    elif choose == "0":
        pass
    else:
        print("Вы ввели что-то не так")

check_data()
print ("meesege for test Git")
menu()