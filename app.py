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

# Создаем две вкладки
tab1, tab2 = st.tabs(["📋 Регистрация выдачи", "🗂️ Просмотр базы и Аналитика"])

with tab1:
    st.header("Новая запись о выдаче корма")
    st.caption("Поля, отмеченные звездочкой (*), обязательны для заполнения")
    
    # Создаем форму для ввода данных
    with st.form("recipient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Основная информация (ФИО и Район)**")
            # ОБЯЗАТЕЛЬНЫЕ ПОЛЯ ФИО
            last_name = st.text_input("Фамилия *")
            first_name = st.text_input("Имя *")
            # НЕОБЯЗАТЕЛЬНОЕ ПОЛЕ
            middle_name = st.text_input("Отчество (По желанию)")
            
            # ОБЯЗАТЕЛЬНОЕ ПОЛЕ РАЙОНА
            district = st.selectbox(
                "Район проживания в Барнауле *", 
                ["Индустриальный", "Ленинский", "Железнодорожный", "Октябрьский", "Центральный"]
            )
            
            st.write("---")
            st.markdown("**Паспортные данные (По желанию)**")
            p_series = st.text_input("Серия паспорта (4 цифры)", max_chars=4)
            p_number = st.text_input("Номер паспорта (6 цифр)", max_chars=6)
            
        with col2:
            st.markdown("**Дополнительные данные (По желанию)**")
            p_date = st.text_input("Дата выдачи паспорта (ДД.ММ.ГГГГ)")
            p_code = st.text_input("Код подразделения", max_chars=7)
            
            st.write("---")
            address = st.text_input("Адрес проживания (Улица, дом, кв)")
            vk_link = st.text_input("Ссылка на профиль ВК")
            feed_type = st.text_input("Какой корм выдан (например, Для кошек 5кг)")
            
        st.write("---")
        submit_button = st.form_submit_button("📁 Шаг 1: Зафиксировать текстовые поля")

    st.write("---")
    
    # Интерактивные модули (ввод даты и телефона) находятся под основной формой, 
    # так как они обновляют экран при каждом нажатии кнопок на планшете
    
    # Модуль выбора даты рождения (По желанию)
    birth_date_str = dp.render_date_picker(label="Дата рождения получателя (По желанию)", key_prefix="main_birth")
    
    # Модуль экранной клавиатуры для телефона (ОБЯЗАТЕЛЬНОЕ ПОЛЕ)
    st.write("---")
    st.markdown("**Номер телефона получателя \***")
    phone_number = pi.render_phone_keyboard()
    
    st.write("---")
    st.subheader("🚀 Шаг 3: Финальное сохранение в базу")
    
    if st.button("✅ ПОЛНОСТЬЮ СОХРАНИТЬ ЗАПИСЬ", type="primary"):
        # Проверяем строго обязательные поля
        if not last_name.strip():
            st.error("Критическая ошибка! Поле 'Фамилия' не может быть пустым.")
        elif not first_name.strip():
            st.error("Критическая ошибка! Поле 'Имя' не может быть пустым.")
        elif not phone_number:
            st.error("Критическая ошибка! Номер телефона обязателен (10 цифр после +7).")
        else:
            # Собираем красивую строку ФИО для базы данных
            # Если отчество есть, добавляем его, если нет — пишем только Фамилию и Имя
            if middle_name.strip():
                full_fio = f"{last_name.strip()} {first_name.strip()} {middle_name.strip()}"
            else:
                full_fio = f"{last_name.strip()} {first_name.strip()}"
            
            # Заполняем пустые паспортные данные уникальными значениями, чтобы избежать ошибок БД
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
            
            # Сохраняем готовую запись в БД
            success = db.add_recipient(new_record)
            if success:
                st.success(f"Запись для {full_fio} успешно добавлена в систему!")
                # Очищаем телефонную сессию для следующего посетителя
                st.session_state.phone_digits = ""
                st.rerun()
            else:
                st.error("Критическая ошибка при генерации уникального ID для базы данных.")

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
