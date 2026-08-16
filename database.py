import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

DB_NAME = "shelter_data.db"

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
            visit_date TEXT, -- Новое поле: дата получения корма
            UNIQUE(passport_series, passport_number)
        )
    """)
    conn.commit()
    conn.close()

def add_recipient(data_dict):
    """Добавляет запись. Если visit_date не передан, ставит сегодняшнюю дату."""
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

def show_admin_panel():
    """Отображает панель с фильтрами и расширенной сортировкой."""
    st.title("🗂️ База данных приюта")

    init_db()
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM recipients", conn)
    conn.close()

    if df.empty:
        st.info("База данных пока пуста.")
        return

    st.subheader("🔍 Фильтрация, поиск и сортировка")
    col1, col2 = st.columns(2)

    with col1:
        search_fio = st.text_input("Поиск по ФИО или телефону")
        districts = ["Все"] + list(df["district"].unique())
        selected_district = st.selectbox("Фильтр по району", districts)

    with col2:
        # Новые инструменты сортировки
        sort_options = {
            "Сначала новые визиты": ("visit_date", False),
            "Сначала старые визиты": ("visit_date", True),
            "По алфавиту (ФИО)": ("fio", True),
            "По дате рождения (от старших)": ("birth_date", True),
            "По дате рождения (от младших)": ("birth_date", False)
        }
        selected_sort = st.selectbox("Сортировка данных", list(sort_options.keys()))

    # Применение фильтров
    filtered_df = df.copy()
    if search_fio:
        filtered_df = filtered_df[
            filtered_df['fio'].str.contains(search_fio, case=False, na=False) | 
            filtered_df['phone'].str.contains(search_fio, na=False)
        ]
    if selected_district != "Все":
        filtered_df = filtered_df[filtered_df['district'] == selected_district]

    # Применение сортировки через Pandas
    sort_column, ascending_order = sort_options[selected_sort]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending_order)

    st.subheader(f"📋 Найдено записей: {len(filtered_df)} из {len(df)}")
    st.dataframe(filtered_df)

if __name__ == "__main__":
    show_admin_panel()
