import streamlit as st
import pandas as pd
from datetime import datetime

WEEKDAYS_RU = {
    0: "1. Понедельник", 1: "2. Вторник", 2: "3. Среда", 
    3: "4. Четверг", 4: "5. Пятница", 5: "6. Суббота", 6: "7. Воскресенье"
}

def init_db():
    """Инициализирует защищенную базу данных в памяти сессии Streamlit."""
    if "shelter_records" not in st.session_state:
        # Создаем пустой датафрейм со всеми нужными колонками
        st.session_state.shelter_records = pd.DataFrame(columns=[
            "fio", "birth_date", "passport_series", "passport_number",
            "passport_date", "passport_code", "phone", "district",
            "vk_link", "address", "feed_type", "photo_path", "visit_date"
        ])

def add_recipient(data_dict):
    """Сохраняет запись во внутреннюю синхронизированную базу данных."""
    init_db()
    df = st.session_state.shelter_records
    
    # Проверка на дубликаты по номеру паспорта
    if data_dict['passport_series'] != "0000":
        duplicate = df[
            (df['passport_series'].astype(str) == str(data_dict['passport_series'])) & 
            (df['passport_number'].astype(str) == str(data_dict['passport_number']))
        ]
        if not duplicate.empty:
            return False
            
    # Добавляем строку в общую память
    new_row = pd.DataFrame([data_dict])
    st.session_state.shelter_records = pd.concat([df, new_row], ignore_index=True)
    return True

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
    
    df = st.session_state.shelter_records

    if df.empty or len(df) == 0:
        st.info("Архив базы данных пуст.")
        return

    # Генерация аналитических колонок
    df['Возраст'] = df['birth_date'].apply(calculate_age)
    df['День недели визита'] = df['visit_date'].apply(get_weekday_name)

    search_fio = st.text_input("Поиск (ФИО / телефон)", placeholder="Введите текст...")
    
    # --- МУЛЬТИВЫБОР ВСЕХ ОФИЦИАЛЬНЫХ РАЙОНОВ БАРНАУЛА ---
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

    df['visit_date_parsed'] = pd.to_datetime(df['visit_date']).dt.date
    min_date, max_value = df['visit_date_parsed'].min(), df['visit_date_parsed'].max()
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

    # --- СТРОГАЯ ФИЛЬТРАЦИЯ ДАННЫХ ---
    filtered_df = df.copy()
    if search_fio:
        filtered_df = filtered_df[filtered_df['fio'].astype(str).str.contains(search_fio, case=False, na=False) | filtered_df['phone'].astype(str).str.contains(search_fio, na=False)]
    
    # Фильтрация по мультивыбору районов Барнаула
    if selected_districts:
        filtered_df = filtered_df[filtered_df['district'].isin(selected_districts)]
        
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['visit_date_parsed'] >= start_date) & (filtered_df['visit_date_parsed'] <= end_date)]

    # Применение выбранной сортировки
    sort_column, ascending_order = sort_options[selected_sort]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending_order)
    filtered_df = filtered_df.drop(columns=['visit_date_parsed'])
    filtered_df['Возраст'] = filtered_df['Возраст'].apply(lambda x: "Не указан" if x == 999 else x)

    st.write("---")
    st.caption(f"НАЙДЕНО ЗАПИСЕЙ В БАЗЕ: {len(filtered_df)}")

    # Вывод карточек получателей по клику
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
                    p_url = parts[0].replace("Человек: ", "")
                    r_url = parts[1].replace("Расписка: ", "")
                    
                    st.link_button("Просмотреть фото получателя", p_url, use_container_width=True)
                    st.link_button("Просмотреть фото расписки", r_url, use_container_width=True)
                except Exception:
                    st.text(f"Ссылки: {row['photo_path']}")
