import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, date

DB_NAME = "shelter_data.db"

WEEKDAYS_RU = {
    0: "1. Понедельник", 1: "2. Вторник", 2: "3. Среда", 
    3: "4. Четверг", 4: "5. Пятница", 5: "6. Соббота", 6: "7. Воскресенье"
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT, birth_date TEXT, passport_series TEXT, passport_number TEXT,
            passport_date TEXT, passport_code TEXT, phone TEXT, district TEXT,
            vk_link TEXT, address TEXT, feed_type TEXT, photo_path TEXT, visit_date TEXT,
            UNIQUE(passport_series, passport_number)
        )
    """)
    conn.commit()
    conn.close()

def add_recipient(data_dict):
    init_db()
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
    try:
        if not birth_date_str or birth_date_str == "Не указана": return 999
        bd = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except Exception: return 999

def get_weekday_name(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return WEEKDAYS_RU[dt.weekday()]
    except Exception: return "Не определен"

def show_admin_panel():
    st.caption("АРХИВ И АНАЛИТИКА")
    init_db()
    
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM recipients", conn)
    conn.close()

    # Фильтры и сортировки показываем всегда, даже если данных пока 0
    search_fio = st.text_input("Поиск (ФИО / телефон)", placeholder="Введите текст...")
    
    all_barnaul_districts = [
        "Железнодорожный", 
        "Индустриальный", 
        "Ленинский", 
        "Октябрьский", 
        "Центральный", 
        "Не определен"
    ]
    
    selected_districts = st.multiselect(
        "Фильтр по районам города (оставьте пустым для выбора всех районов)", 
        options=all_barnaul_districts,
        default=[]
    )

    if not df.empty:
        df['visit_date_parsed'] = pd.to_datetime(df['visit_date']).dt.date
        min_date, max_value = df['visit_date_parsed'].min(), df['visit_date_parsed'].max()
    else:
        min_date, max_value = date.today(), date.today()

    date_range = st.date_input("Период посещения", value=(min_date, max_value), min_value=min_date, max_value=max_value)

    sort_options = {
        "Сначала новые визиты": ("visit_date", False),
        "Сначала старые визиты": ("visit_date", True),
        "По районам города (А-Я)": ("district", True),
        "По дням недели визита (Пн-Вс)": ("День недели визита", True),
        "От старших к младшим (Возраст)": ("Возраст", True),
        "По алфавиту (ФИО)": ("fio", True)
    }
    selected_sort = st.selectbox("Сортировка списка", list(sort_options.keys()))

    if df.empty or len(df) == 0:
        st.write("---")
        st.info("В базе данных пока нет сохраненных записей. Добавьте первую запись на вкладке 'Ввод данных'.")
        return

    df['Возраст'] = df['birth_date'].apply(calculate_age)
    df['День недели визита'] = df['visit_date'].apply(get_weekday_name)

    filtered_df = df.copy()
    if search_fio:
        filtered_df = filtered_df[filtered_df['fio'].astype(str).str.contains(search_fio, case=False, na=False) | filtered_df['phone'].astype(str).str.contains(search_fio, na=False)]
    
    if selected_districts:
        filtered_df = filtered_df[filtered_df['district'].isin(selected_districts)]
        
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['visit_date_parsed'] >= start_date) & (filtered_df['visit_date_parsed'] <= end_date)]

    sort_column, ascending_order = sort_options[selected_sort]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending_order)
    filtered_df = filtered_df.drop(columns=['visit_date_parsed'])
    filtered_df['Возраст'] = filtered_df['Возраст'].apply(lambda x: "Не указан" if x == 999 else x)

    st.write("---")
    st.caption(f"НАЙДЕНО ЗАПИСЕЙ В БАЗЕ: {len(filtered_df)}")

    for index, row in filtered_df.iterrows():
        with st.expander(f"👤 {row['fio']} | {row['district']} район"):
            st.markdown(f"**Контакты:** {row['phone']}")
            st.markdown(f"**Дата визита:** {row['visit_date']}")
            
            st.write("---")
            st.caption("ПОЛНАЯ АНКЕТА ПОЛУЧАТЕЛЯ")
            st.text(f"Возраст: {row['Возраст']} (д.р. {row['birth_date']})")
            st.text(f"Адрес: {row['address']}")
            st.text(f"Выданный корм: {row['feed_type']}")
            st.text(f"Паспорт: {row['passport_series']} {row['passport_number']}")
            
            st.write("---")
            st.caption("ССЫЛКИ НА МАТЕРИАЛЫ В ВК")
            if row['vk_link'] and row['vk_link'] != "Не указана":
                st.link_button("Личный профиль ВК", str(row['vk_link']), use_container_width=True)
                
            if "Человек:" in str(row['photo_path']):
                try:
                    parts = str(row['photo_path']).split(" | ")
                    p_url = parts.replace("Человек: ", "")
                    r_url = parts.replace("Расписка: ", "")
                    
                    st.link_button("Просмотреть фото получателя", p_url, use_container_width=True)
                    st.link_button("Просмотреть фото расписки", r_url, use_container_width=True)
                except Exception:
                    st.text(f"Ссылки: {row['photo_path']}")
