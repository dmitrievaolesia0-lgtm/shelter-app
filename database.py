import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

DB_NAME = "shelter_data.db"

# Словарь для перевода дней недели на русский язык
WEEKDAYS_RU = {
    0: "1. Понедельник",
    1: "2. Вторник",
    2: "3. Среда",
    3: "4. Четверг",
    4: "5. Пятница",
    5: "6. Суббота",
    6: "7. Воскресенье"
}

def init_db():
    """Создает базу данных и таблицу с учетом даты выдачи корма."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT,
            birth_date TEXT,
            passport_series TEXT,
            passport_number TEXT,
            passport_date TEXT,
            passport_code TEXT,
            phone TEXT,
            district TEXT,
            vk_link TEXT,
            address TEXT,
            feed_type TEXT,
            photo_path TEXT,
            visit_date TEXT,
            UNIQUE(passport_series, passport_number)
        )
    """)
    conn.commit()
    conn.close()

def add_recipient(data_dict):
    """Добавляет запись в базу данных."""
    if 'visit_date' not in data_dict or not data_dict['visit_date']:
        data_dict['visit_date'] = datetime.today().strftime('%Y-%m-%d')
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO recipients (fio, birth_date, passport_series, passport_number, 
                                    passport_date, passport_code, phone, district, 
                                    vk_link, address, feed_type, photo_path, visit_date)
            VALUES (:fio, :birth_date, :passport_series, :passport_number, 
                    :passport_date, :passport_code, :phone, :district, 
                    :vk_link, :address, :feed_type, :photo_path, :visit_date)
        """, data_dict)
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def calculate_age(birth_date_str):
    """Вычисляет возраст на основе строки даты (ГГГГ-ММ-ДД)."""
    try:
        if not birth_date_str or birth_date_str == "Не указана":
            return 999
        bd = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except Exception:
        return 999

def get_weekday_name(date_str):
    """Определяет день недели по дате."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return WEEKDAYS_RU[dt.weekday()]
    except Exception:
        return "Не определен"

def show_admin_panel():
    """Отображает панель с продвинутой фильтрацией и сортировкой для телефона."""
    st.title("🗂️ База данных приюта")

    init_db()
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM recipients", conn)
    conn.close()

    if df.empty:
        st.info("База данных пока пуста.")
        return

    # Добавляем виртуальные столбцы для продвинутой сортировки
    df['Возраст'] = df['birth_date'].apply(calculate_age)
    df['День недели визита'] = df['visit_date'].apply(get_weekday_name)

    st.subheader("🔍 Фильтрация, поиск и сортировка")
    
    search_fio = st.text_input("Поиск по ФИО или телефону")
    
    districts = ["Все"] + list(df["district"].unique())
    selected_district = st.selectbox("Фильтр по району", districts)

    # Календарный фильтр периодов визитов
    st.write("---")
    st.markdown("**📅 Выберите период посещения:**")
    df['visit_date_parsed'] = pd.to_datetime(df['visit_date']).dt.date
    min_date, max_date = df['visit_date_parsed'].min(), df['visit_date_parsed'].max()
    
    date_range = st.date_input("Диапазон дат визитов", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    # Выбор расширенной сортировки (Добавили сортировку по районам!)
    st.write("---")
    sort_options = {
        "Сначала новые визиты ⏳": ("visit_date", False),
        "Сначала старые визиты ⌛": ("visit_date", True),
        "По районам города (А-Я) 🏙️": ("district", True), # <-- НОВОЕ Поле сортировки!
        "По дням недели визита (Пн-Вс) 🗓️": ("День недели визита", True),
        "От старших к младшим (Возраст ↓) 👴": ("Возраст", True),
        "От младших к старшим (Возраст ↑) 👶": ("Возраст", False),
        "По алфавиту (ФИО) 🔤": ("fio", True)
    }
    selected_sort = st.selectbox("📊 Выберите тип сортировки списка:", list(sort_options.keys()))

    # --- ПРИМЕНЕНИЕ ФИЛЬТРОВ ---
    filtered_df = df.copy()
    if search_fio:
        filtered_df = filtered_df[
            filtered_df['fio'].str.contains(search_fio, case=False, na=False) | 
            filtered_df['phone'].str.contains(search_fio, na=False)
        ]
    if selected_district != "Все":
        filtered_df = filtered_df[filtered_df['district'] == selected_district]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['visit_date_parsed'] >= start_date) & (filtered_df['visit_date_parsed'] <= end_date)]

    # --- ПРИМЕНЕНИЕ СОРТИРОВКИ ---
    sort_column, ascending_order = sort_options[selected_sort]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending_order)

    # Очищаем датафрейм от вспомогательных служебных колонок
    filtered_df = filtered_df.drop(columns=['visit_date_parsed'])
    filtered_df['Возраст'] = filtered_df['Возраст'].apply(lambda x: "Не указан" if x == 999 else x)

    st.subheader(f"📋 Найдено записей: {len(filtered_df)} из {len(df)}")
    st.dataframe(filtered_df, use_container_width=True)

if __name__ == "__main__":
    show_admin_panel()
