
import sqlite3
import pandas as pd

# Инициализация базы данных SQLite на устройстве
def init_db():
    conn = sqlite3.connect('shelter_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_delivery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            feed_type TEXT NOT NULL,
            delivery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Функция добавления записи
def add_record(name, phone, feed):
    try:
        conn = sqlite3.connect('shelter_data.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO food_delivery (client_name, phone, feed_type) VALUES (?, ?, ?)", 
            (name, phone, feed)
        )
        conn.commit()
        conn.close()
        print(f"✅ Успешно добавлено: {name}")
    except sqlite3.IntegrityError:
        print("⚠️ Ошибка: Этот номер телефона уже есть в базе данных!")

# Выгрузка в Excel
def export_to_excel():
    conn = sqlite3.connect('shelter_data.db')
    df = pd.read_sql_query("SELECT * FROM food_delivery", conn)
    conn.close()
    df.to_excel("отчет_приюта.xlsx", index=False)
    print("🎉 База успешно сохранена в файл 'отчет_приюта.xlsx'")

if __name__ == "__main__":
    init_db()
    print("🐾 Система приюта инициализирована!")
  
