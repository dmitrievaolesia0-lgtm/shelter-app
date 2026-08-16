import streamlit as st

def get_user_inputs():
    st.markdown("""
        <style>
        html, body, [class*="css"], .stWidgetFormProp {
            font-family: Arial, Helvetica, sans-serif !important;
        }
        /* Стили для красивого счетчика телефона */
        .phone-counter {
            font-size: 0.8rem;
            color: #666;
            margin-top: -15px;
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Базовые личные данные
    last_name = st.text_input("Фамилия *")
    first_name = st.text_input("Имя *")
    middle_name = st.text_input("Отчество (по желанию)")
    
    # Дата рождения строго в одну строчку через компактные колонки
    st.markdown("Дата рождения *")
    col1, col2, col3 = st.columns([1, 1, 1.5])
    with col1:
        birth_day = st.text_input("День", placeholder="ДД", label_visibility="collapsed")
    with col2:
        birth_month = st.text_input("Месяц", placeholder="ММ", label_visibility="collapsed")
    with col3:
        birth_year = st.text_input("Год", placeholder="ГГГГ", label_visibility="collapsed")
    
    # Поле телефона со счетчиком введенных цифр
    phone_raw = st.text_input("Телефон *", key="phone_buffer")
    
    # Считаем только цифры в введенном тексте
    digits_only = "".join(filter(str.isdigit, phone_raw))
    digits_count = len(digits_only)
    
    # Подсказка под полем (динамически обновляется)
    st.markdown(
        f'<div class="phone-counter">Введено цифр: <b>{digits_count}</b> (например, нужно 11 для 79991234567)</div>', 
        unsafe_allow_html=True
    )
    
    # ИЗМЕНЕНО: Район Барнаула в виде выпадающего списка
    barnaul_districts = [
        "Железнодорожный",
        "Индустриальный",
        "Ленинский",
        "Октябрьский",
        "Центральный"
    ]
    district = st.selectbox("Район Барнаула *", options=barnaul_districts)
    
    # Адрес (необязательное поле)
    address = st.text_input("Адрес (улица, дом, кв. — необязательно)", placeholder="например, ул. Ленина, д. 10, кв. 5")
    
    # Предпочтения
    feed_type = st.selectbox("Тип корма *", options=["Сухой", "Влажный", "Лечебный"])

    # Склеиваем дату в стандартный формат
    birth_date_str = f"{birth_day}.{birth_month}.{birth_year}" if (birth_day or birth_month or birth_year) else ""

    return {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_date": birth_date_str,
        "phone_raw": phone_raw,
        "district": district,
        "address": address,
        "feed_type": feed_type
    }
