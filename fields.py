import streamlit as st
from datetime import date

def get_user_inputs():
    st.markdown("""
        <style>
        html, body, [class*="css"], .stWidgetFormProp {
            font-family: Arial, Helvetica, sans-serif !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Базовые личные данные
    last_name = st.text_input("Фамилия *")
    first_name = st.text_input("Имя *")
    middle_name = st.text_input("Отчество (по желанию)")
    
    # ИЗМЕНЕНО: Полноценный ввод даты рождения с визуальной подсказкой формата
    # Используем date_input. Значение по умолчанию — None, чтобы симулировать пустой плейсхолдер
    birth_date = st.date_input(
        "Дата рождения *",
        value=None,
        format="DD.MM.YYYY",
        placeholder="ДД.ММ.ГГГГ"
    )
    
    # Контакты
    phone_raw = st.text_input("Телефон *", key="phone_buffer")
    
    # ДОБАВЛЕНО: Район проживания
    district = st.text_input("Район *")
    
    # ДОБАВЛЕНО: Адрес (необязательное поле)
    address = st.text_input("Адрес (необязательно)")
    
    # Предпочтения
    feed_type = st.selectbox("Тип корма *", options=["Сухой", "Влажный", "Лечебный"])

    # Функция возвращает обновленный словарь со всеми ключами
    return {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_date": birth_date,  # Возвращает объект datetime.date или None
        "phone_raw": phone_raw,
        "district": district,
        "address": address,
        "feed_type": feed_type
    }
