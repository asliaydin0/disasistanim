import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv(override=True)

def get_db_connection():
    print("--- BAĞLANTI BİLGİLERİ ---")
    print(f"Host: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 3306)}")
    print(f"Kullanıcı: {os.getenv('DB_USER')}")
    print("--------------------------")

    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS") or "",
            database=os.getenv("DB_NAME"),
            use_pure=True  # Sorunlu C çekirdeğini devre dışı bıraktık
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None