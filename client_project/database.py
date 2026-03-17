import psycopg2


def get_connection():
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='postgres',
        database='clients_db'
    )

    return conn