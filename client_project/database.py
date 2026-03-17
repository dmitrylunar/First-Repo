import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        database=os.getenv('DB_NAME', 'clients_db')
    )
