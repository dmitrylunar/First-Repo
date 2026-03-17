import time
from services import add_client, save_client, client_list, find_client, delete_finding_client, send_bulk_email

def menu():
    while True:
        print("\nВыберете операцию: "
              "\n1 - Добавить клиента"
              "\n2 - Посмотреть всю базу"
              "\n3 - Найти клиента"
              "\n4 - Удалить клиента"
              "\n5 - Сделать рассылку"
              "\n0 - Выход")
        choose = input("Ввод: ")
        if choose == "1":
            save_client(add_client())
        elif choose == "2":
            client_list()
        elif choose == "3":
            search = input("Введите данные для поиска: ")
            results = find_client(search)
            if results:
                for p in results:
                    print(f"ID: {p[0]} \nИмя: {p[1]}\nНомер: {p[2]}\nПочта: {p[3]}\n")
            else:
                print("Совпадений не найдено")
        elif choose == "4":
            delete_finding_client()
        elif choose == "5":
            subject = input("Тема письма: ")
            message = input("Текст письма: ")
            send_bulk_email(subject, message)
        elif choose == "0":
            print("Завершение программы...")
            break
        else:
            print("Вы ввели что-то не так")
        time.sleep(1.5)

menu()