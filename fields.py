import streamlit as st

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
    
    # ИЗМЕНЕНО: Наглядный ввод даты рождения по частям с плейсхолдерами
    st.markdown("Дата рождения *")
    col1, col2, col3 = st.columns(3)
    with col1:
        birth_day = st.text_input("День", placeholder="ДД", label_visibility="collapsed")
    with col2:
        birth_month = st.text_input("Месяц", placeholder="ММ", label_visibility="collapsed")
    with col3:
        birth_year = st.text_input("Год", placeholder="ГГГГ", label_visibility="collapsed")
    
    # Контакты
    phone_raw = st.text_input("Телефон *", key="phone_buffer")
    
    # Район проживания
    district = st.text_input("Район *")
    
    # Адрес (необязательное поле)
    address = st.text_input("Адрес (необязательно)")
    
    # Предпочтения
    feed_type = st.selectbox("Тип корма *", options=["Сухой", "Влажный", "Лечебный"])

    # Функция возвращает словарь, объединяя дату в единую строку или сохраняя раздельно
    birth_date_str = f"{birth_day}.{birth_month}.{birth_year}" if (birth_day or birth_month or birth_year) else ""

    return {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_date": birth_date_str,  # Итоговая строка вида "ДД.ММ.ГГГГ"
        "phone_raw": phone_raw,
        "district": district,
        "address": address,
        "feed_type": feed_type
    }
