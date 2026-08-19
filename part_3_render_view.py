import streamlit as st
import pandas as pd
import db_analytics as analytics
import part_4_render_details_and_actions as p4

DISTRICT_MAP = {
    "Железнодорожный": "ЖД", "Индустриальный": "ИНД", "Ленинский": "ЛЕН",
    "Октябрьский": "ОКТ", "Центральный": "ЦЕНТР", "Не определен": "Н/А"
}

WEEKDAY_MAP = {
    "Понедельник": "ПН", "Вторник": "ВТ", "Среда": "СР", 
    "Четверг": "ЧТ", "Пятница": "ПТ", "Суббота": "СБ", "Воскресенье": "ВС"
}

def part_3_render_view(filtered_df, df):
    """Часть 3: Высокоскоростной, монохромный и строго регламентированный вывод данных."""
    if filtered_df.empty:
        st.info("По заданным критериям поиска записей не найдено.")
        return

    def get_short_district(dist_name):
        return DISTRICT_MAP.get(str(dist_name).strip(), "Н/А")

    def get_short_weekday(day_name):
        return WEEKDAY_MAP.get(str(day_name).strip(), "-")

    st.caption("ℹ️ Нажмите на любую строку с ФИО ниже, чтобы открыть анкету человека")
    
    for idx, row in filtered_df.iterrows():
        fio_text = row.get('fio', 'Без имени')
        phone_val = row.get('phone', '-')
        short_dist = get_short_district(row.get('district', 'Не определен'))
        
        row_header = f"{fio_text}  |  {phone_val}  |  Район: {short_dist}"
        
        with st.expander(row_header, expanded=False):
            current_district = row.get('district', 'Не определен')
            render_single_card_contents(
                row, phone_val, current_district, idx, df, get_short_weekday
            )

def render_single_card_contents(row, current_phone, current_district, idx, df, get_short_weekday_func):
    """Системный блок вывода внутренних параметров субъекта без жирного шрифта"""
    phone_to_call = current_phone if current_phone else row.get('phone', '-')
    
    try:
        callable_phone = analytics.make_phone_callable(phone_to_call)
    except (NameError, AttributeError):
        callable_phone = phone_to_call
    
    st.markdown(f"Номер телефона: {callable_phone}", unsafe_allow_html=True)
    
    short_day = get_short_weekday_func(row.get('День недели визита', '-'))
    st.markdown(f"Дата визита: {row.get('visit_date', '-')} ({short_day})")
    st.markdown(f"Район проживания: {current_district}")
    st.markdown(f"Номенклатура выданного корма: {row.get('feed_type', '-')}")
    
    photo_str = row.get('photo_path', '')
    photo_str = "" if pd.isna(photo_str) else str(photo_str).strip()
    
    photo_person, photo_receipt = "Не указана", "Не указана"
    if photo_str and "|" in photo_str:
        try:
            parts = photo_str.split("|")
            for part in parts:
                if "Человек:" in part: 
                    photo_person = part.replace("Человек:", "").strip()
                if "Расписка:" in part: 
                    photo_receipt = part.replace("Расписка:", "").strip()
        except Exception:
            pass
    
    links_html = []
    if photo_person != "Не указана" and photo_person.strip().startswith("http"):
        links_html.append(
            f'<a href="{photo_person.strip()}" target="_blank" '
            f'style="color: #2C3E50; text-decoration: underline;">Фото получателя</a>'
        )
    if photo_receipt != "Не указана" and photo_receipt.strip().startswith("http"):
        links_html.append(
            f'<a href="{photo_receipt.strip()}" target="_blank" '
            f'style="color: #2C3E50; text-decoration: underline;">Фото расписки</a>'
        )
   
    try:
        p4.part_4_render_details_and_actions(links_html, row, current_district, idx, df)
    except (NameError, AttributeError) as e:
        st.error(f"Не удалось загрузить блок действий (Часть 4): {e}")
