import streamlit as st

def get_user_inputs():
    st.markdown("""
        <style>
        html, body, [class*="css"], .stWidgetFormProp {
            font-family: Arial, Helvetica, sans-serif !important;
        }
        /* Стили для полоски-индикатора телефона */
        .phone-progress-bg {
            background-color: #e0e0e0;
            border-radius: 4px;
            height: 6px;
            width: 100%;
            margin-top: -12px;
            margin-bottom: 6px;
            overflow: hidden;
        }
        .phone-progress-bar {
            height: 100%;
            transition: width 0.3s ease, background-color 0.3s ease;
        }
        .phone-status-text {
            font-size: 0.8rem;
            margin-bottom: 15px;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    # Личные данные
    last_name = st.text_input("Фамилия *")
    first_name = st.text_input("Имя *")
    middle_name = st.text_input("Отчество (по желанию)")
    
    # ИЗМЕНЕНО: Одно единое поле для даты рождения с подсказкой внутри
    birth_date_str = st.text_input("Дата рождения *", placeholder="ДД.ММ.ГГГГ")
    
    # Поле телефона
    phone_raw = st.text_input("Телефон *", key="phone_buffer", placeholder="79991234567")
    
    # Считаем только введенные цифры
    digits_only = "".join(filter(str.isdigit, phone_raw))
    digits_count = len(digits_only)
    target_digits = 11  # Стандарт для РФ (например, 79991234567)
    
    # Рассчитываем процент заполнения полоски (максимум 100%)
    progress_percent = min((digits_count / target_digits) * 100, 100)
    
    # Определяем цвет полоски и текст в зависимости от количества цифр
    if digits_count == 0:
        bar_color = "#e0e0e0"
        status_text = f"<span style='color: #666;'>Осталось ввести: <b>{target_digits}</b> цифр</span>"
    elif digits_count < target_digits:
        # Если введено мало — красный, если уже ближе к концу — оранжевый/желтый
        bar_color = "#ff4b4b" if digits_count < 7 else "#ffa500"
        status_text = f"<span style='color: {bar_color};'>Введено: {digits_count}. Осталось ввести: <b>{target_digits - digits_count}</b> цифр</span>"
    elif digits_count == target_digits:
        bar_color = "#28a745" # Зеленый
        status_text = "<span style='color: #28a745;'><b>Отлично! Все 11 цифр введены.</b></span>"
    else:
        bar_color = "#ff4b4b" # Снова красный, если переборщили
        status_text = f"<span style='color: #ff4b4b;'><b>Лишние цифры!</b> Введено {digits_count} вместо {target_digits}</span>"

    # Выводим полочку-индикатор и статус под полем телефона
    st.markdown(f"""
        <div class="phone-progress-bg">
            <div class="phone-progress-bar" style="width: {progress_percent}%; background-color: {bar_color};"></div>
        </div>
        <div class="phone-status-text">{status_text}</div>
    """, unsafe_allow_html=True)
    
    # Район Барнаула
    barnaul_districts = ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный"]
    district = st.selectbox("Район Барнаула *", options=barnaul_districts)
    
    # Адрес (необязательное поле)
    address = st.text_input("Адрес (улица, дом, кв. — необязательно)", placeholder="например, ул. Ленина, д. 10, кв. 5")
    
    # Предпочтения
    feed_type = st.selectbox("Тип корма *", options=["Сухой", "Влажный", "Лечебный"])

    # Возвращаем старый ключ "birth_year", чтобы у вас не падала ошибка KeyError в файле app.py
    return {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_year": birth_date_str,  # Здесь теперь лежит вся строка даты из одного поля
        "phone_raw": phone_raw,
        "district": district,
        "address": address,
        "feed_type": feed_type
    }

