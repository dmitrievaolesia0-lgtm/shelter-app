import streamlit as st
import pandas as pd
from datetime import datetime
import yandex_cloud as cloud

# Чистые строгие названия дней недели для графиков и карточек
WEEKDAYS_RU = {
    0: "Понедельник", 1: "Вторник", 2: "Среда", 
    3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"
}

@st.cache_data(show_spinner="Загрузка базы данных из облака Яндекс...", ttl=300)
def cached_download():
    """Сверхбыстрое скачивание с официальным кэшированием в памяти."""
    df = cloud.download_from_yandex()
    if df is not None and not df.empty:
        # Принудительно очищаем от битых строк, где нет ключевых данных, и сбрасываем индекс
        if 'fio' in df.columns and 'phone' in df.columns:
            df = df.dropna(subset=['fio', 'phone'])
        df = df.reset_index(drop=True)
        return df
    return pd.DataFrame()


def clear_db_cache():
    """Точечная очистка кэша только для функции загрузки базы данных."""
    cached_download.clear()


def init_db():
    """Инициализация базы данных пустым шаблоном, если она отсутствует."""
    df = cached_download()
    if df.empty:
        empty_df = cloud.get_empty_template()
        cloud.upload_to_yandex(empty_df)
        clear_db_cache()


def add_recipient(data_dict):
    """Безопасное добавление нового получателя с проверкой на дубликаты."""
    if 'visit_date' not in data_dict or not data_dict['visit_date']:
        data_dict['visit_date'] = datetime.now().strftime('%Y-%m-%d')
        
    df = cached_download()
    
    # Если база пустая — создаем первую строчку
    if df.empty:
        new_row_df = pd.DataFrame([data_dict]).reset_index(drop=True)
        success = cloud.upload_to_yandex(new_row_df)
        clear_db_cache()
        return success
        
    curr_fio = str(data_dict.get('fio', '')).strip().lower()
    curr_phone = str(data_dict.get('phone', '')).strip().lower()
    
    # Проверка на дубликаты
    if curr_fio and curr_phone:
        db_fio = df['fio'].astype(str).str.strip().str.lower()
        db_phone = df['phone'].astype(str).str.strip().str.lower()
        
        duplicate = df[(db_fio == curr_fio) & (db_phone == curr_phone)]
        if not duplicate.empty:
            st.warning("⚠️ Этот человек с таким номером телефона уже зарегистрирован в базе.")
            return False

    new_row_df = pd.DataFrame([data_dict])
    # Объединяем и строго сбрасываем индексы перед сохранением в облако
    updated_df = pd.concat([df, new_row_df], ignore_index=True).reset_index(drop=True)
    
    success = cloud.upload_to_yandex(updated_df)
    clear_db_cache()
    return success


def calculate_age(birth_date_str):
    """Вычисление возраста. Возвращает 999, если дата некорректна."""
    try:
        if not birth_date_str or pd.isna(birth_date_str):
            return 999
        if str(birth_date_str).strip() in ["Не указана", "Не указан", ""]: 
            return 999
            
        bd = pd.to_datetime(birth_date_str).date()
        today = datetime.now().date()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except Exception:
        return 999


def get_weekday_name(date_str):
    """Определение текстового дня недели по дате типа ГГГГ-ММ-ДД."""
    try:
        if not date_str or pd.isna(date_str):
            return "Не определен"
        dt = pd.to_datetime(date_str)
        return WEEKDAYS_RU[dt.weekday()]
    except Exception: 
        return "Не определен"


def make_vk_deeplink(vk_url):
    """Преобразует стандартную ссылку ВК в мобильный диплинк для открытия в приложении."""
    if not vk_url or pd.isna(vk_url):
        return None
        
    url_str = str(vk_url).strip()
    if url_str in ["Не указана", "Не указан", ""]:
        return None
        
    if url_str.startswith("vk://"):
        return url_str
        
    cleaned = url_str.replace("https://", "").replace("http://", "").replace("www.", "")
    return f"vk://{cleaned}"


def update_recipient_comment(record_index, text_value):
    """Системное и физическое обновление текстового комментария в ячейке Яндекс Облака."""
    try:
        df = cached_download()
        
        # Защита: проверяем, существует ли физически строка с таким индексом
        if df is not None and not df.empty and record_index in df.index:
            df.at[record_index, 'comment_text'] = str(text_value).strip()
            
            # Отправка обновленной таблицы обратно в Яндекс.Облако
            success = cloud.upload_to_yandex(df)
            if success:
                clear_db_cache()  # Сбрасываем кэш, чтобы при следующем запросе скачался новый файл
                return True
        return False
    except Exception:
        return False
