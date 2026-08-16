import streamlit as st
import pandas as pd
from datetime import datetime, date
import yandex_cloud as cloud  # Подключаем наш первый файл

WEEKDAYS_RU = {
    0: "1. Понедельник", 1: "2. Вторник", 2: "3. Среда", 
    3: "4. Четверг", 4: "5. Пятница", 5: "6. Суббота", 6: "7. Воскресенье"
}

def init_db():
    df = cloud.download_from_yandex()
    # Если файла на Яндекс.Диске нет или он пустой — создаем его с правильной структурой
    if df.empty or len(df) == 0:
        empty_df = cloud.get_empty_template()
        cloud.upload_to_yandex(empty_df)

def add_recipient(data_dict):
    if 'visit_date' not in data_dict or not data_dict['visit_date']:
        data_dict['visit_date'] = datetime.today().strftime('%Y-%m-%d')
        
    df = cloud.download_from_yandex()
    
    # Полностью очищаем базу от возможных пустых строк (NaN), которые создает Excel
    if not df.empty:
        df = df.dropna(subset=['fio', 'phone']).reset_index(drop=True)
    
    # Если база пустая — никакие дубликаты физически не проверяем, сразу сохраняем!
    if df.empty or len(df) == 0:
        new_row_df = pd.DataFrame([data_dict])
        return cloud.upload_to_yandex(new_row_df)
        
    curr_fio = str(data_dict.get('fio', '')).strip().lower()
    curr_phone = str(data_dict.get('phone', '')).strip().lower()
    
    # Проверка на дубликат строго по ФИО + Номер телефона
    if curr_fio and curr_phone:
        db_fio = df['fio'].astype(str).str.strip().str.lower()
        db_phone = df['phone'].astype(str).str.strip().str.lower()
        
        duplicate = df[(db_fio == curr_fio) & (db_phone == curr_phone)]
        if not duplicate.empty:
            st.warning("⚠️ Этот человек с таким номером телефона уже зарегистрирован в базе.")
            return False

    # Если дубликатов нет, добавляем строку к очищенной таблице и загружаем
    new_row_df = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_row_df], ignore_index=True)
    return cloud.upload_to_yandex(updated_df)

def calculate_age(birth_date_str):
    try:
        if not birth_date_str or pd.isna(birth_date_str) or birth_date_str in ["Не указана", "Не указан", ""]: 
            return 999
        bd = pd.to_datetime(birth_date_str).date()
        today = datetime.today().date()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except: 
        return 999

def get_weekday_name(date_str):
    try:
        dt = pd.to_datetime(date_str)
        return WEEKDAYS_RU[dt.weekday()]
    except: 
        return "Не определен"

def show_admin_panel():
    st.caption("АРХИВ И АНАЛИТИКА (ОБЛАКО ЯНДЕКС)")
    if st.button("🔄 Обновить данные из облака"):
        st.rerun()
        
    df = cloud.download_from_yandex()
    if not df.empty and 'fio' in df.columns and 'phone' in df.columns:
        df = df.dropna(subset=['fio', 'phone']).reset_index(drop=True)
        
    search_fio = st.text_input("Поиск (ФИО / телефон)", placeholder="Введите текст...")
    all_barnaul_districts = ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]
    selected_districts = st.multiselect("Фильтр по районам города", options=all_barnaul_districts, default=[])

    if not df.empty and 'visit_date' in df.columns:
        df['visit_date_parsed'] = pd.to_datetime(df['visit_date'], errors='coerce').dt.date
        min_date, max_value = df['visit_date_parsed'].min(), df['visit_date_parsed'].max()
        if pd.isna(min_date): min_date = date.today()
        if pd.isna(max_value): max_value = date.today()
    else:
        min_date, max_value = date.today(), date.today()

    if min_date > max_value: min_date = max_value
    date_range = st.date_input("Период посещения", value=(min_date, max_value), min_value=min_date, max_value=max_value)

    sort_options = {
        "Сначала новые визиты": ("visit_date", False),
        "Сначала старые визиты": ("visit_date", True),
        "По районам города (А-Я)": ("district", True),
        "От старших к младшим (Возраст)": ("Возраст", True),
        "По алфавиту (ФИО)": ("fio", True)
    }
    selected_sort = st.selectbox("Сортировка списка", list(sort_options.keys()))

    if df.empty or len(df) == 0:
        st.write("---")
        st.info("Архив базы данных пуст.")
        return

    df['Возраст'] = df['birth_date'].apply(calculate_age)
    df['День недели визита'] = df['visit_date'].apply(get_weekday_name)

    filtered_df = df.copy()
    if search_fio:
        filtered_df = filtered_df[
            filtered_df['fio'].astype(str).str.contains(search_fio, case=False, na=False) | 
            filtered_df['phone'].astype(str).str.contains(search_fio, na=False)
        ]
    
    if selected_districts:
        filtered_df = filtered_df[filtered_df['district'].isin(selected_districts)]
        
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['visit_date_parsed'] >= start_date) & (filtered_df['visit_date_parsed'] <= end_date)]

    sort_column, ascending_order = sort_options[selected_sort]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending_order)
    
    if 'visit_date_parsed' in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=['visit_date_parsed'])
        
    filtered_df['Возраст'] = filtered_df['Возраст'].apply(lambda x: "Не указан" if x == 999 else x)
    st.session_state.shelter_records = filtered_df

    st.write("---")
    st.caption(f"НАЙДЕНО ЗАПИСЕЙ В БАЗЕ: {len(filtered_df)}")

    for index, row in filtered_df.iterrows():
        with st.expander(f"👤 {row.get('fio', 'Без имени')} | {row.get('district', 'Не определен')} район"):
            st.markdown(f"**Контакты:** {row.get('phone', '-')}")
            st.markdown(f"**Дата визита:** {row.get('visit_date', '-')}")
            st.write("---")
            st.caption("ПОЛНАЯ АНКЕТА ПОЛУЧАТЕЛЯ")
            st.text(f"Возраст: {row.get('Возраст')} (д.р. {row.get('birth_date', '-')})")
            st.text(f"Адрес: {row.get('address', '-')}")
            st.text(f"Выданный корм: {row.get('feed_type', '-')}")
            st.text(f"Паспорт: {row.get('passport_series', '-')} {row.get('passport_number', '-')}")
