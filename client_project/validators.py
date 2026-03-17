def valid_name(name):
    while name == "" or not name.isalpha():
        name = input("Имя клиента должно содержать только буквы!\nВведите имя: ")
    return name

def valid_number(number):
    while number == "" or not number.isdigit() or len(number) != 11:
        number = input('Введите корректный номер из 11 цифр!\nВедите номер: ')
    return number

def valid_email(email):
    while email == "":
        email = input('Введите email: ')
    return email

def valid_id(id):
    while id == "" or not id.isdigit():
        id = input('Введите корректный id: ')
    return id