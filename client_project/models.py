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