import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date

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
    
    # 1. ФИО полностью обязательное
    last_name = st.text_input("Фамилия *", key="reg_last_name")
    first_name = st.text_input("Имя *", key="reg_first_name")
    middle_name = st.text_input("Отчество *", key="reg_middle_name")
    
    # 2. Район проживания
    district = st.selectbox(
        "Район проживания в Барнауле *", 
        ["Индустриальный", "Ленинский", "Железнодорожный", "Октябрьский", "Центральный"],
        key="reg_district"
    )
    
    # 3. ДАТА ВИЗИТА (Новое поле для переноса данных из тетради!)
    # По умолчанию стоит сегодняшний день, но календарь позволяет выбрать прошлые даты
    visit_date_selected = st.date_input(
        "📅 Дата визита (для старых записей выберите нужный день) *",
        value=date.today(),
        max_value=date.today(), # Нельзя выбрать дату из будущего
        key="reg_visit_date"
    )
    
    # 4. Номер телефона в общем стиле
    st.write("---")
    phone_number = pi.render_phone_keyboard()
    
    # 5. НЕОБЯЗАТЕЛЬНЫЕ ДАННЫЕ
    st.write("---")
    st.markdown("### ⚪ НЕОБЯЗАТЕЛЬНЫЕ ДАННЫЕ (По желанию)")
    
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
        elif not middle_name.strip():
            st.error("Заполните Отчество!")
        elif not phone_number:
            st.error("Введите ПОЛНЫЙ номер телефона (нажмите на поле телефона выше)!")
        else:
            # Собираем полное ФИО
            full_fio = f"{last_name.strip()} {first_name.strip()} {middle_name.strip()}"
            
            # Защита базы от пустых паспортов
            final_series = p_series.strip() if p_series.strip() else "0000"
            final_number = p_number.strip() if p_number.strip() else f"б/н-{int(datetime.timestamp(datetime.now()))}"
            
            # Форматируем выбранную дату в строку для базы данных
            visit_date_str = visit_date_selected.strftime('%Y-%m-%d')
            
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
                "visit_date": visit_date_str # Сохраняем дату, которую выбрал волонтер
            }
            
            success = db.add_recipient(new_record)
            if success:
                st.success(f"Успешно сохранено для: {full_fio} за дату {visit_date_selected.strftime('%d.%m.%Y')}")
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
