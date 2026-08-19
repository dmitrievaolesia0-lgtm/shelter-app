import streamlit as st
import pandas as pd
import re
from datetime import datetime, date

import database as db
import date_picker as dp
import map_barnaul as mb
import db_admin 
import db_recovery as rec

# Настройка страницы с адаптивным размещением под разные экраны
st.set_page_config(page_title="Учет выдачи корма", layout="centered")

st.markdown("""
    <style>
        /* Увеличенный верхний отступ предотвращает наложение шапки Streamlit на планшетах */
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

# Заголовок системы со смещением вниз
st.markdown('<div class="custom-title">Система регистрации и учета выдачи корма</div>', unsafe_allow_html=True)

# Инициализируем флаг успешного сохранения, чтобы управлять кнопками навигации
if "save_success_flag" not in st.session_state:
    st.session_state.save_success_flag = False

# Очистка формы через прямое удаление старых значений из памяти
def reset_form_fields():
    for key in ["input_last_name", "input_first_name", "input_middle_name", "input_phone", "input_photo_person", "input_photo_receipt"]:
        if key in st.session_state:
            st.session_state[key] = ""

tab1, tab2 = st.tabs(["ВВОД ДАННЫХ", "АРХИВ И АНАЛИТИКА"])

# --- ВКЛАДКА 1: ВВОД ДАННЫХ ---
with tab1:
    # Если запись только что успешно сохранилась — выводим меню навигации
    if st.session_state.save_success_flag:
        st.success("Уведомление: Данные успешно внесены в базу данных.")
        st.write("Выберите следующее действие для продолжения:")
        
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("Добавить еще человека", key="btn_add_more_success", use_container_width=True):
                st.session_state.save_success_flag = False
                reset_form_fields()
                st.rerun()
        with col_nav2:
            if st.button("Перейти в архив", key="btn_go_to_archive_success", use_container_width=True):
                st.session_state.save_success_flag = False
                reset_form_fields()
                st.info("Пожалуйста, нажмите на вкладку 'АРХИВ И АНАЛИТИКА' вверху экрана.")
    
    else:
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
                    try:
                        import db_core
                        current_df = db_core.cached_download()
                        recovery_manager = rec.SystemRecoveryManager()
                        recovery_manager.execute_dump(current_df)
                    except Exception:
                        pass

                    st.cache_data.clear()
                    st.session_state.save_success_flag = True
                    st.rerun()
                else:
                    st.error("Ошибка: Обнаружен дубликат. Запись с аналогичными ФИО и номером телефона уже существует.")

# --- ВКЛАДКА 2: АРХИВ И АНАЛИТИКА ---
with tab2:
    db_admin.show_admin_panel()
    st.write("---")
    if "shelter_records" in st.session_state and not st.session_state.shelter_records.empty:
        mb.render_barnaul_map(st.session_state.shelter_records)
