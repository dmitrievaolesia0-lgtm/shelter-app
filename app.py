import streamlit as st
import pandas as pd
import sqlite3
import re
from datetime import datetime, date

import database as db
import date_picker as dp
import map_barnaul as mb

# Настройка страницы для мобильных телефонов
st.set_page_config(page_title="Приют КОРМ", layout="centered")
db.init_db()

st.title("🐾 Учет выдачи корма")

# Вкладки для телефона
tab1, tab2 = st.tabs(["📋 Выдача корма", "🗂️ База и Карта"])

with tab1:
    st.markdown("### 🔴 ОБЯЗАТЕЛЬНЫЕ ДАННЫЕ")
    
    # Ввод ФИО
    last_name = st.text_input("Фамилия *", placeholder="Иванов")
    first_name = st.text_input("Имя *", placeholder="Иван")
    middle_name = st.text_input("Отчество *", placeholder="Иванович")
    
    district = st.selectbox(
        "Район проживания в Барнауле *", 
        ["Индустриальный", "Ленинский", "Железнодорожный", "Октябрьский", "Центральный", "Не определен"]
    )
    
    visit_date_selected = st.date_input(
        "📅 Дата визита *",
        value=date.today(),
        max_value=date.today()
    )
    
    st.write("---")
    # --- УМНЫЙ ВВОД ТЕЛЕФОНА БЕЗ ТОРМОЗЯЩИХ КНОПОК ---
    st.markdown("**Номер телефона \***")
    
    # Переключатель формата номера
    phone_mode = st.radio(
        "Формат номера:",
        ["Стандартный мобильный РФ (+7)", "Иной формат (городской / другая страна)"],
        horizontal=True
    )
    
    if phone_mode == "Стандартный мобильный РФ (+7)":
        # Волонтер вводит только 10 цифр без +7, программа сама подсказывает формат
        raw_phone = st.text_input(
            "Введите 10 цифр номера (после +7) *", 
            placeholder="9991234567",
            max_chars=10
        )
        
        # Очищаем ввод от случайных пробелов или букв, оставляем только цифры
        digits_only = re.sub(r"\D", "", raw_phone)
        
        if len(digits_only) == 10:
            # Формируем красивый финальный номер для базы данных
            final_phone = f"+7 ({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:8]}-{digits_only[8:10]}"
            st.success(f"Формат верный: {final_phone}")
            phone_error = None
        elif len(digits_only) > 0:
            st.warning(f"⚠️ Введено цифр: {len(digits_only)} из 10. Нужно ровно 10 цифр.")
            phone_error = "ОШИБКА_ДЛИНЫ"
            final_phone = ""
        else:
            phone_error = "НЕ_ЗАПОЛНЕН"
            final_phone = ""
    else:
        # Режим «Иной номер» — полная свобода ввода без ограничений по длине
        custom_phone = st.text_input(
            "Введите номер телефона в любом формате вручную *", 
            placeholder="Например: +7 (3852) 12-34-56 или +77..."
        )
        if custom_phone.strip():
            final_phone = custom_phone.strip()
            phone_error = None
        else:
            phone_error = "НЕ_ЗАПОЛНЕН"
            final_phone = ""

    st.write("---")
    st.markdown("### 📸 ФОТОФИКСАЦИЯ ВЫДАЧИ *")
    photo_person_link = st.text_input("Ссылка на фото человека *", placeholder="https://vk.com...")
    photo_receipt_link = st.text_input("Ссылка на фото расписки *", placeholder="https://vk.com...")
    
    st.write("---")
    st.markdown("### ⚪ НЕОБЯЗАТЕЛЬНЫЕ ДАННЫЕ (По желанию)")
    
    address = st.text_input("Адрес проживания (Улица, дом)")
    vk_link = st.text_input("Ссылка на личный ВК получателя")
    feed_type = st.text_input("Какой корм выдан (Например: Кэт Чау 3кг)")
    
    st.write("---")
    st.markdown("**Паспортные данные**")
    p_series = st.text_input("Серия паспорта", max_chars=4, placeholder="0000")
    p_number = st.text_input("Номер паспорта", max_chars=6, placeholder="000000")
    p_date = st.text_input("Дата выдачи паспорта", placeholder="ДД.ММ.ГГГГ")
    p_code = st.text_input("Код подразделения", max_chars=7, placeholder="000-000")
    
    birth_date_str = dp.render_date_picker(label="Дата рождения", key_prefix="main_birth")
    
    st.write("---")
    if st.button("🔥 СОХРАНИТЬ ЗАПИСЬ", type="primary", use_container_width=True):
        # Проверка обязательных полей
        if not last_name.strip():
            st.error("Заполните Фамилию!")
        elif not first_name.strip():
            st.error("Заполните Имя!")
        elif not middle_name.strip():
            st.error("Заполните Отчество!")
        # Проверки телефона
        elif phone_error == "НЕ_ЗАПОЛНЕН":
            st.error("Укажите номер телефона получателя!")
        elif phone_error == "ОШИБКА_ДЛИНЫ":
            st.error("Критическая ошибка! В стандартном номере должно быть ровно 10 цифр. Исправьте ошибку или переключите формат на 'Иной формат'.")
        elif not photo_person_link.strip():
            st.error("Вставьте ссылку на фотографию человека!")
        elif not photo_receipt_link.strip():
            st.error("Вставьте ссылку на фотографию расписки!")
        else:
            full_fio = f"{last_name.strip()} {first_name.strip()} {middle_name.strip()}"
            
            final_series = p_series.strip() if p_series.strip() else "0000"
            final_number = p_number.strip() if p_number.strip() else f"б/н-{int(datetime.timestamp(datetime.now()))}"
            visit_date_str = visit_date_selected.strftime('%Y-%m-%d')
            
            combined_photos = f"Человек: {photo_person_link.strip()} | Расписка: {photo_receipt_link.strip()}"
            
            new_record = {
                "fio": full_fio,
                "birth_date": birth_date_str if birth_date_str else "Не указана",
                "passport_series": final_series,
                "passport_number": final_number,
                "passport_date": p_date.strip() if p_date.strip() else "Не указана",
                "passport_code": p_code.strip() if p_code.strip() else "Не указан",
                "phone": final_phone, # Сохраняем проверенный и отформатированный номер
                "district": district,
                "vk_link": vk_link.strip() if vk_link.strip() else "Не указана",
                "address": address.strip() if address.strip() else "Не указан",
                "feed_type": feed_type.strip() if feed_type.strip() else "Не указан",
                "photo_path": combined_photos,
                "visit_date": visit_date_str
            }
            
            success = db.add_recipient(new_record)
            if success:
                st.success(f"Успешно сохранено для: {full_fio}")
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
