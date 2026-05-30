import psycopg2
from psycopg2.extras import RealDictCursor

# Функция для получения соединения с базой
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="curs_korochka", # Имя твоей базы
            user="postgres",      # Твой пользователь
            password="Sergey980270", # Твой пароль
            host="127.0.0.1",
            port="5432",
            client_encoding='utf8' # Принудительно просим UTF-8
        )
        return conn
    except Exception as e:
        # repr(e) покажет сырой текст ошибки без падения кодировки
        print(f"Истинная ошибка подключения: {repr(e)}")
        return None
    
if __name__ == "__main__":
    print("Попробуем подключиться к базе данных")
    conn = get_db_connection()
    if conn:
        print("✅ Успех! Подключение к PostgreSQL работает.")
        conn.close()
    else:
        print("❌ Не работает. Смотри текст ошибки выше.")