def consolidate(func):
    def wrapper(*args, **kwargs):
        print("Выполнить операцию? Y/N :")
        par = input("Ввод: ")
        if par.lower() == "y":
            return func(*args, **kwargs)
        print("Операция отменена...")
        return None
    return wrapper