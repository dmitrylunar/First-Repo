import re

# ── Для интерактивного ввода (зацикливаются до корректного значения) ────────

def valid_name(name):
    while not name or not name.replace(' ', '').isalpha():
        name = input("Имя должно содержать только буквы!\nВведите имя: ")
    return name

def valid_number(number):
    while not number or not number.isdigit() or len(number) != 11:
        number = input('Введите корректный номер из 11 цифр!\nВведите номер: ')
    return number

def valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    while not email or not re.match(pattern, email):
        email = input('Введите корректный email (например user@mail.ru): ')
    return email

def valid_id(id):
    while not id or not id.isdigit():
        id = input('Введите корректный id: ')
    return id

# ── Для валидации из файла (возвращают True/False, не зацикливаются) ────────

def is_valid_name(name):
    return bool(name) and str(name).replace(' ', '').isalpha()

def is_valid_number(number):
    if not number:
        return False
    try:
        number_str = str(int(float(str(number))))
        return number_str.isdigit() and len(number_str) == 11
    except (ValueError, TypeError):
        return False

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return bool(email) and bool(re.match(pattern, str(email)))