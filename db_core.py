import streamlit as st
import pandas as pd
from datetime import datetime
import yandex_cloud as cloud

WEEKDAYS_RU = {
    0: "Понедельник", 1: "Вторник", 2: "Среда", 
    3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"
}

@st.cache_data(show_spinner="Загрузка базы данных из облака Яндекс...")
def cached_download():
    """Сверхбыстрое скачивание с кэшированием в оперативной памяти."""
    df = cloud.download_from_yandex()
    if not df.empty and 'fio' in df.columns and 'phone' in df.columns:
        df = df.dropna(subset=['fio', 'phone']).reset_index(drop=True)
    return df

def clear_db_cache():
    """Очищает кэш для принудительного обновления данных."""
    st.cache_data.clear()

def init_db():
    df = cached_download()
    if df.empty or len(df) == 0:
        empty_df = cloud.get_empty_template()
        cloud.upload_to_yandex(empty_df)
        clear_db_cache()

def add_recipient(data_dict):
    if 'visit_date' not in data_dict or not data_dict['visit_date']:
        data_dict['visit_date'] = datetime.today().strftime('%Y-%m-%d')
        
    df = cached_download()
    
    if df.empty or len(df) == 0:
        new_row_df = pd.DataFrame([data_dict])
        success = cloud.upload_to_yandex(new_row_df)
        clear_db_cache()
        return success
        
    curr_fio = str(data_dict.get('fio', '')).strip().lower()
    curr_phone = str(data_dict.get('phone', '')).strip().lower()
    
    if curr_fio and curr_phone:
        db_fio = df['fio'].astype(str).str.strip().str.lower()
        db_phone = df['phone'].astype(str).str.strip().str.lower()
        
        duplicate = df[(db_fio == curr_fio) & (db_phone == curr_phone)]
        if not duplicate.empty:
            st.warning("⚠️ Этот человек с таким номером телефона уже зарегистрирован в базе.")
            return False

    new_row_df = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_row_df], ignore_index=True)
    success = cloud.upload_to_yandex(updated_df)
    clear_db_cache()
    return success

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
