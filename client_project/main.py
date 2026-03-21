import time
import os
from services import (add_client, save_client, client_list, find_client,
                      delete_finding_client, send_bulk_email,
                      get_databases_list, load_database_from_excel, delete_database)

def menu():
    while True:
        print("\nВыберете операцию: "
              "\n1 - Добавить клиента"
              "\n2 - Посмотреть всю базу"
              "\n3 - Найти клиента"
              "\n4 - Удалить клиента"
              "\n5 - Сделать рассылку"
              "\n6 - Загрузить базу из Excel"
              "\n7 - Посмотреть список баз"
              "\n8 - Удалить базу"
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
            databases = get_databases_list()
            if databases:
                print("\nДоступные базы:")
                for db_id, db_name, total in databases:
                    print(f"  [{db_id}] {db_name} — {total} контактов")
                print("  [0] Вся база")
                choice = input("\nВведите db_id или 0 для всей базы: ").strip()
                if not choice:
                    print("Ввод не может быть пустым")
                    time.sleep(1.5)
                    continue
                db_id = None if choice == "0" else (int(choice) if choice.isdigit() else None)
                if db_id is None and choice != "0":
                    print("Введите корректный id")
                    time.sleep(1.5)
                    continue
            else:
                print("Загруженных баз нет — рассылка по всей базе")
                db_id = None
            subject = input("Тема письма: ").strip()
            if not subject:
                print("Тема письма не может быть пустой")
                time.sleep(1.5)
                continue
            message = input("Текст письма: ").strip()
            if not message:
                print("Текст письма не может быть пустым")
                time.sleep(1.5)
                continue
            send_bulk_email(subject, message, db_id)

        elif choose == "6":
            file_path = input("Путь к Excel файлу: ").strip()
            if not file_path:
                print("Путь к файлу не может быть пустым")
            elif not file_path.endswith('.xlsx'):
                print("Файл должен быть в формате .xlsx")
            elif not os.path.exists(file_path):
                print(f"Файл не найден: {file_path}")
            else:
                db_name = input("Название базы: ").strip()
                if not db_name:
                    print("Название базы не может быть пустым")
                else:
                    try:
                        added, skipped = load_database_from_excel(file_path, db_name)
                        print(f"Готово! Добавлено: {added}, пропущено: {skipped}")
                    except Exception as e:
                        print(f"Ошибка при загрузке файла: {e}")

        elif choose == "7":
            databases = get_databases_list()
            if databases:
                print("\nЗагруженные базы:")
                for db_id, db_name, total in databases:
                    print(f"  [{db_id}] {db_name} — {total} контактов")
            else:
                print("Загруженных баз нет")

        elif choose == "8":
            databases = get_databases_list()
            if not databases:
                print("Загруженных баз нет")
            else:
                print("\nЗагруженные базы:")
                for db_id, db_name, total in databases:
                    print(f"  [{db_id}] {db_name} — {total} контактов")
                db_name = input("Введите название базы для удаления: ").strip()
                if not db_name:
                    print("Название базы не может быть пустым")
                else:
                    confirm = input(f"Удалить базу '{db_name}'? Y/N: ").strip().lower()
                    if confirm == "y":
                        try:
                            count = delete_database(db_name)
                            if count:
                                print(f"База '{db_name}' удалена, {count} контактов удалено")
                            else:
                                print("База с таким названием не найдена")
                        except Exception as e:
                            print(f"Ошибка при удалении базы: {e}")
                    else:
                        print("Отменено")

        elif choose == "0":
            print("Завершение программы...")
            break

        else:
            print("Вы ввели что-то не так")

        time.sleep(1.5)

menu()