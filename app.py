import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date

import database as db
import phone_input as pi
import date_picker as dp
import map_barnaul as mb

st.set_page_config(page_title="Приют КОРМ", layout="centered")
db.init_db()

st.title("🐾 Учет выдачи корма")

tab1, tab2 = st.tabs(["📋 Выдача", "🗂️ База и Карта"])

with tab1:
    st.markdown("### 🔴 ОБЯЗАТЕЛЬНЫЕ ДАННЫЕ")
    
    last_name = st.text_input("Фамилия *", key="reg_last_name")
    first_name = st.text_input("Имя *", key="reg_first_name")
    middle_name = st.text_input("Отчество *", key="reg_middle_name")
    
    # Добавлен район "Не определен"
    district = st.selectbox(
        "Район проживания в Барнауле *", 
        ["Индустриальный", "Ленинский", "Железнодорожный", "Октябрьский", "Центральный", "Не определен"],
        key="reg_district"
    )
    
    visit_date_selected = st.date_input(
        "📅 Дата визита *",
        value=date.today(),
        max_value=date.today(),
        key="reg_visit_date"
    )
    
    st.write("---")
    phone_number = pi.render_phone_keyboard()
    
    # НОВЫЙ БЛОК: Обязательные ссылки на фотоотчет (ВК / Диск)
    st.write("---")
    st.markdown("### 📸 ФОТОФИКСАЦИЯ ВЫДАЧИ *")
    st.caption("Загрузите фото в альбом ВК или Облако и вставьте ссылки ниже:")
    photo_person_link = st.text_input("Ссылка на фото человека *", placeholder="https://vk.com...")
    photo_receipt_link = st.text_input("Ссылка на фото расписки *", placeholder="https://vk.com...")
    
    st.write("---")
    st.markdown("### ⚪ НЕОБЯЗАТЕЛЬНЫЕ ДАННЫЕ (По желанию)")
    
    address = st.text_input("Адрес проживания (Улица, дом)")
    vk_link = st.text_input("Ссылка на личный ВК получателя")
    feed_type = st.text_input("Какой корм выдан (Например: Кэт Чау 3кг)")
    
    st.write("---")
    st.markdown("**Паспортные данные**")
    p_series = st.text_input("Серия паспорта", max_chars=4)
    p_number = st.text_input("Номер паспорта", max_chars=6)
    p_date = st.text_input("Дата выдачи паспорта")
    p_code = st.text_input("Код подразделения", max_chars=7)
    
    birth_date_str = dp.render_date_picker(label="Дата рождения", key_prefix="main_birth")
    
    st.write("---")
    if st.button("🔥 СОХРАНИТЬ ЗАПИСЬ", type="primary", use_container_width=True):
        if not last_name.strip():
            st.error("Заполните Фамилию!")
        elif not first_name.strip():
            st.error("Заполните Имя!")
        elif not middle_name.strip():
            st.error("Заполните Отчество!")
        elif phone_number == "НЕ_ЗАПОЛНЕН":
            st.error("Укажите номер телефона получателя!")
        elif phone_number == "ОШИБКА_ДЛИНЫ":
            st.error("Ошибка в длине номера телефона!")
        # Проверка заполнения ссылок на фотографии
        elif not photo_person_link.strip():
            st.error("Вставьте ссылку на фотографию человека!")
        elif not photo_receipt_link.strip():
            st.error("Вставьте ссылку на фотографию расписки!")
        else:
            full_fio = f"{last_name.strip()} {first_name.strip()} {middle_name.strip()}"
            
            final_series = p_series.strip() if p_series.strip() else "0000"
            final_number = p_number.strip() if p_number.strip() else f"б/н-{int(datetime.timestamp(datetime.now()))}"
            visit_date_str = visit_date_selected.strftime('%Y-%m-%d')
            
            # Объединяем две ссылки в одну строку для хранения в существующем поле photo_path базы данных
            combined_photos = f"Человек: {photo_person_link.strip()} | Расписка: {photo_receipt_link.strip()}"
            
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
                "photo_path": combined_photos, # Сохраняем ссылки в базу
                "visit_date": visit_date_str
            }
            
            success = db.add_recipient(new_record)
            if success:
                st.success(f"Успешно сохранено для: {full_fio}")
                st.session_state.phone_digits = ""
                st.session_state.is_other_format = False
                st.session_state.other_phone_text = ""
                st.rerun()
            else:
                st.error("Ошибка дублирования данных или сбой БД.")

with tab2:
    db.show_admin_panel()
    st.write("---")
    conn = sqlite3.connect(db.DB_NAME)
    current_df = pd.read_sql_query("SELECT district FROM recipients", conn)
    conn.close()
    mb.render_barnaul_map(current_df)
