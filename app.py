import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Импортируем наши созданные модули
import database as db
import phone_input as pi
import date_picker as dp
import map_barnaul as mb

# Настройка страницы под экраны смартфонов
st.set_page_config(page_title="Приют КОРМ", layout="centered")

# Инициализируем базу данных
db.init_db()

st.title("🐾 Учет выдачи корма")

# Две вкладки для телефона
tab1, tab2 = st.tabs(["📋 Выдача", "🗂️ База и Карта"])

with tab1:
    st.markdown("### 🔴 ОБЯЗАТЕЛЬНЫЕ ДАННЫЕ")
    
    # 1. ФИО по отдельности
    last_name = st.text_input("Фамилия *", key="reg_last_name")
    first_name = st.text_input("Имя *", key="reg_first_name")
    
    # 2. Район проживания
    district = st.selectbox(
        "Район проживания в Барнауле *", 
        ["Индустриальный", "Ленинский", "Железнодорожный", "Октябрьский", "Центральный"],
        key="reg_district"
    )
    
    # 3. Номер телефона (Кнопки появятся только при активации тумблера внутри модуля)
    st.write("---")
    phone_number = pi.render_phone_keyboard()
    
    # 4. НЕОБЯЗАТЕЛЬНЫЕ ДАННЫЕ (Пошли ниже, чтобы не мешать на экране телефона)
    st.write("---")
    st.markdown("### ⚪ НЕОБЯЗАТЕЛЬНЫЕ ДАННЫЕ (По желанию)")
    
    middle_name = st.text_input("Отчество (Если есть)")
    address = st.text_input("Адрес проживания (Улица, дом)")
    vk_link = st.text_input("Ссылка на ВК")
    feed_type = st.text_input("Какой корм выдан (Например: Кэт Чау 3кг)")
    
    st.write("---")
    st.markdown("**Паспортные данные**")
    p_series = st.text_input("Серия паспорта", max_chars=4)
    p_number = st.text_input("Номер паспорта", max_chars=6)
    p_date = st.text_input("Дата выдачи паспорта")
    p_code = st.text_input("Код подразделения", max_chars=7)
    
    # Модуль выбора даты рождения
    st.write("---")
    birth_date_str = dp.render_date_picker(label="Дата рождения", key_prefix="main_birth")
    
    # КНОПКА СОХРАНЕНИЯ
    st.write("---")
    if st.button("🔥 СОХРАНИТЬ ЗАПИСЬ", type="primary", use_container_width=True):
        # Проверяем строго обязательные поля
        if not last_name.strip():
            st.error("Заполните Фамилию!")
        elif not first_name.strip():
            st.error("Заполните Имя!")
        elif not phone_number:
            st.error("Введите ПОЛНЫЙ номер телефона (откройте клавиши выше)!")
        else:
            # Собираем ФИО
            if middle_name.strip():
                full_fio = f"{last_name.strip()} {first_name.strip()} {middle_name.strip()}"
            else:
                full_fio = f"{last_name.strip()} {first_name.strip()}"
            
            # Защита базы от пустых паспортов
            final_series = p_series.strip() if p_series.strip() else "0000"
            final_number = p_number.strip() if p_number.strip() else f"б/н-{int(datetime.timestamp(datetime.now()))}"
            
            new_record = {
                "fio": full_fio,
                "birth_date": birth_date_str if birth_date_str else "Не указана",
                "passport_series": final_series,
                "passport_number": final_number,
                "passport_date": p_date.strip() if p_date.strip() else "Не указана",
                "passport_code": p_code.strip() if p_code.strip() else "Не указан",
                "phone": phone_number,
                "district": district,
                "vk_link": vk_link.strip() if vk_link.strip() else "Не указана",
                "address": address.strip() if address.strip() else "Не указан",
                "feed_type": feed_type.strip() if feed_type.strip() else "Не указан",
                "photo_path": "No photo",
                "visit_date": datetime.today().strftime('%Y-%m-%d')
            }
            
            success = db.add_recipient(new_record)
            if success:
                st.success(f"Успешно сохранено для: {full_fio}")
                # Сброс номера телефона для следующего человека
                st.session_state.phone_digits = ""
                st.rerun()
            else:
                st.error("Ошибка дублирования данных или сбой БД.")

with tab2:
    # База данных адаптированная под телефон
    db.show_admin_panel()
    st.write("---")
    
    # Карта Барнаула
    conn = sqlite3.connect(db.DB_NAME)
    current_df = pd.read_sql_query("SELECT district FROM recipients", conn)
    conn.close()
    mb.render_barnaul_map(current_df)
