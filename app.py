import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Импортируем наши созданные модули
import database as db
import phone_input as pi
import date_picker as dp
import map_barnaul as mb

# Настройка страницы для удобной работы на планшете
st.set_page_config(page_title="Приют - Выдача корма", layout="wide")

# Инициализируем базу данных при старте приложения
db.init_db()

st.title("🐾 Система учета выдачи корма в приюте")

# Создаем две вкладки: для работы волонтера и для просмотра базы
tab1, tab2 = st.tabs(["📋 Регистрация выдачи", "🗂️ Просмотр базы и Аналитика"])

with tab1:
    st.header("Новая запись о выдаче корма")
    
    # Создаем форму для ввода данных
    with st.form("recipient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fio = st.text_input("ФИО получателя (Полностью)")
            
            st.write("---")
            st.markdown("**Паспортные данные**")
            p_series = st.text_input("Серия паспорта (4 цифры)", max_chars=4)
            p_number = st.text_input("Номер паспорта (6 цифр)", max_chars=6)
            p_date = st.text_input("Дата выдачи паспорта (ДД.ММ.ГГГГ)")
            p_code = st.text_input("Код подразделения", max_chars=7)
            
        with col2:
            district = st.selectbox(
                "Район проживания в Барнауле", 
                ["Индустриальный", "Ленинский", "Железнодорожный", "Октябрьский", "Centralный"]
            )
            address = st.text_input("Адрес проживания (Улица, дом, кв)")
            vk_link = st.text_input("Ссылка на профиль ВК")
            feed_type = st.text_input("Какой корм выдан (например, Для кошек 5кг)")
            
        st.write("---")
        
        # Кнопка отправки формы
        submit_button = st.form_submit_button("📁 Зафиксировать основные данные")

    st.write("---")
    
    # Сложные интерактивные модули (ввод даты и телефона) выносим под форму, 
    # так как они обновляют экран при каждом нажатии кнопок
    
    # 1. Модуль выбора даты рождения
    birth_date_str = dp.render_date_picker(label="Дата рождения получателя", key_prefix="main_birth")
    
    # 2. Модуль экранной клавиатуры для телефона
    st.write("---")
    phone_number = pi.render_phone_keyboard()
    
    st.write("---")
    st.subheader("🚀 Шаг 3: Финальное сохранение в базу")
    
    if st.button("✅ ПОЛНОСТЬЮ СОХРАНИТЬ ЗАПИСЬ", type="primary"):
        if not fio or not p_series or not p_number:
            st.error("Ошибка! ФИО, серия и номер паспорта обязательны для заполнения.")
        elif not phone_number:
            st.error("Ошибка! Номер телефона должен быть введен полностью (10 цифр после +7).")
        else:
            # Собираем все данные в один словарь для базы данных
            new_record = {
                "fio": fio,
                "birth_date": birth_date_str,
                "passport_series": p_series,
                "passport_number": p_number,
                "passport_date": p_date,
                "passport_code": p_code,
                "phone": phone_number,
                "district": district,
                "vk_link": vk_link,
                "address": address,
                "feed_type": feed_type,
                "photo_path": "No photo", # Пока работаем без фото
                "visit_date": datetime.today().strftime('%Y-%m-%d')
            }
            
            # Отправляем в базу данных
            success = db.add_recipient(new_record)
            if success:
                st.success(f"Запись для {fio} успешно добавлена! Выдача зафиксирована.")
                # Очищаем телефон для следующего ввода
                st.session_state.phone_digits = ""
                st.rerun()
            else:
                st.error("Критическая ошибка: Человек с такими паспортными данными (Серия и Номер) УЖЕ есть в базе! Дубль заблокирован.")

with tab2:
    # Отображаем админ-панель с фильтрами и сортировкой из модуля database.py
    db.show_admin_panel()
    
    st.write("---")
    
    # Подгружаем актуальные данные для карты Барнаула
    conn = sqlite3.connect(db.DB_NAME)
    current_df = pd.read_sql_query("SELECT district FROM recipients", conn)
    conn.close()
    
    # Отображаем карту Барнаула со счетчиками людей по районам
    mb.render_barnaul_map(current_df)
