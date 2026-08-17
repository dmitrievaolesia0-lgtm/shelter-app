import streamlit as st
import pandas as pd
import re
from datetime import datetime, date

import database as db
import date_picker as dp
import map_barnaul as mb
import db_admin 

# Настройка страницы и адаптивных отступов для планшетов
st.set_page_config(page_title="Учет выдачи корма", layout="centered")

st.markdown("""
    <style>
        .block-container {
            padding-top: 4.0rem !important;
            padding-bottom: 0rem !important;
        }
        .custom-title {
            font-size: 20px !important;
            font-weight: 600;
            color: #31333F;
            margin-bottom: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

db.init_db()

# Заголовок системы со смещением вниз для планшетов
st.markdown('<div class="custom-title">Система регистрации и учета выдачи корма</div>', unsafe_allow_html=True)

# Инициализируем переменные для отслеживания шагов в памяти
if "show_success_options" not in st.session_state:
    st.session_state.show_success_options = False
if "saved_fio" not in st.session_state:
    st.session_state.saved_fio = ""

# Функция очистки текстовых полей формы
def reset_form():
    st.session_state["input_last_name"] = ""
    st.session_state["input_first_name"] = ""
    st.session_state["input_middle_name"] = ""
    st.session_state["input_phone"] = ""
    st.session_state["input_photo_person"] = ""
    st.session_state["input_photo_receipt"] = ""
    st.session_state.show_success_options = False

# Понятные и заметные вкладки вверху экрана
tab1, tab2 = st.tabs(["ВВОД ДАННЫХ", "АРХИВ И АНАЛИТИКА"])

# --- ВКЛАДКА 1: ВВОД ДАННЫХ ---
with tab1:
    # Если запись только что успешно сохранилась — показываем меню выбора для оператора
    if st.session_state.show_success_options:
        st.success(f"Уведомление: Данные внесены в базу данных. Субъект: {st.session_state.saved_fio}")
        st.write("---")
        st.write("Выберите дальнейшее действие:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Ввести следующего человека", use_container_width=True):
                reset_form()
                st.rerun()
                
        with col2:
            if st.button("📊 Перейти в архив и аналитику", use_container_width=True):
                # Сбрасываем флаг, очищаем форму и просим пользователя переключить вкладку вверху
                reset_form()
                st.info("Пожалуйста, нажмите на вкладку 'АРХИВ И АНАЛИТИКА' в самом верху экрана.")
        
    else:
        # Обычный режим отображения полей ввода
        last_name = st.text_input("Фамилия", placeholder="Пример: Бортников", key="input_last_name")
        first_name = st.text_input("Имя", placeholder="Пример: Игорь", key="input_first_name")
        middle_name = st.text_input("Отчество", placeholder="Пример: Иванович", key="input_middle_name")
        
        district = st.selectbox(
            "Район проживания в Барнауле", 
            ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]
        )
        
        visit_date_selected = st.date_input(
            "Дата визита",
            value=date.today(),
            max_value=date.today()
        )
        
        st.write("---")
        st.caption("Контактные данные")
        
        user_phone_input = st.text_input(
            "Номер телефона (допускается вставка скопированной строки)", 
            placeholder="89991234567",
            key="input_phone"
        )
        
        phone_error = None
        final_phone = user_phone_input.strip()
        
        if final_phone:
            digits_only = re.sub(r"\D", "", final_phone)
            if len(digits_only) == 11 and (digits_only.startswith("7") or digits_only.startswith("8")):
                main_part = digits_only[1:]
                final_phone = f"+7 ({main_part[:3]}) {main_part[3:6]}-{main_part[6:8]}-{main_part[8:10]}"
                st.caption(f"Формат определен: {final_phone}")
            elif len(digits_only) == 10:
                final_phone = f"+7 ({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:8]}-{digits_only[8:10]}"
                st.caption(f"Формат определен: {final_phone}")
            else:
                st.caption(f"Строка сохранена без изменений: {final_phone}")
        else:
            phone_error = "НЕ_ЗАПОЛНЕН"

        st.write("---")
        st.caption("Фотофиксация (необязательно)")
        photo_person_link = st.text_input("Ссылка на фото получателя", placeholder="https://...", key="input_photo_person")
        photo_receipt_link = st.text_input("Ссылка на фото расписки", placeholder="https://...", key="input_photo_receipt")
        
        st.write("---")
        
        # Главная кнопка действия
        if st.button("Сохранить запись", use_container_width=True):
            if not last_name.strip(): 
                st.error("Ошибка: Поле 'Фамилия' обязательно для заполнения.")
            elif not first_name.strip(): 
                st.error("Ошибка: Поле 'Имя' обязательно для заполнения.")
            elif not middle_name.strip(): 
                st.error("Ошибка: Поле 'Отчество' обязательно для заполнения.")
            elif phone_error == "НЕ_ЗАПОЛНЕН": 
                st.error("Ошибка: Поле 'Номер телефона' обязательно для заполнения.")
            else:
                full_fio = f"{last_name.strip()} {first_name.strip()} {middle_name.strip()}"
                visit_date_str = visit_date_selected.strftime('%Y-%m-%d')
                
                p_link = photo_person_link.strip() if photo_person_link.strip() else "Не указана"
                r_link = photo_receipt_link.strip() if photo_receipt_link.strip() else "Не указана"
                combined_photos = f"Человек: {p_link} | Расписка: {r_link}"
                
                new_record = {
                    "fio": full_fio, 
                    "birth_date": "Не указана",
                    "passport_series": "0000", 
                    "passport_number": f"б/н-{int(datetime.timestamp(datetime.now()))}",
                    "passport_date": "Не указана",
                    "passport_code": "Не указан", 
                    "phone": final_phone, 
                    "district": district,
                    "vk_link": "Не указана",
                    "address": "Не указан",
                    "feed_type": "Не указан",
                    "photo_path": combined_photos, 
                    "visit_date": visit_date_str
                }
                
                success = db.add_recipient(new_record)
                if success:
                    st.cache_data.clear()
                    # Запоминаем имя и переключаем экран в режим выбора действий
                    st.session_state.saved_fio = full_fio
                    st.session_state.show_success_options = True
                    st.rerun()
                else:
                    st.error("Ошибка: Обнаружен дубликат. Запись с аналогичными ФИО и номером телефона уже существует.")

# --- ВКЛАДКА 2: АРХИВ И АНАЛИТИКА ---
with tab2:
    db_admin.show_admin_panel()
    st.write("---")
    
    if "shelter_records" in st.session_state and not st.session_state.shelter_records.empty:
        mb.render_barnaul_map(st.session_state.shelter_records)
