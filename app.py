import streamlit as st
import pandas as pd
import re
from datetime import datetime, date

import database as db
import date_picker as dp
import map_barnaul as mb
import db_admin 

# 1. КРАСИВЫЙ ДИЗАЙН: Убираем гигантский пустой отступ сверху страницы
st.set_page_config(page_title="Учет выдачи корма", layout="centered")

st.markdown("""
    <style>
        /* Сжимаем пустые отступы сверху, чтобы заголовок поднялся выше */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
        }
        div.stSubheader {
            margin-top: 0rem !important;
            padding-top: 0rem !important;
        }
    </style>
""", unsafe_allow_html=True)

db.init_db()

# Наш главный заголовок теперь аккуратно прижат кверху
st.subheader("📝 Регистрация и учет выдачи корма")

tab1, tab2 = st.tabs(["Ввод данных", "Архив и аналитика"])

with tab1:
    st.caption("ОБЯЗАТЕЛЬНЫЕ ДАННЫЕ")
    
    last_name = st.text_input("Фамилия *", placeholder="Бортников")
    first_name = st.text_input("Имя *", placeholder="Игорь")
    middle_name = st.text_input("Отчество *", placeholder="Иванович")
    
    district = st.selectbox(
        "Район проживания в Барнауле *", 
        ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]
    )
    
    visit_date_selected = st.date_input(
        "Дата визита *",
        value=date.today(),
        max_value=date.today()
    )
    
    st.write("---")
    st.caption("КОНТАКТНЫЕ ДАННЫЕ")
    
    # 2. УПРОЩЕНИЕ: Одно поле для телефона. Можно вставлять скопированное как угодно!
    user_phone_input = st.text_input(
        "Номер телефона * (можно просто вставить скопированный номер)", 
        placeholder="8 (999) 123-45-67 или +7999..."
    )
    
    # Логика автоматической очистки вставленного номера
    phone_error = None
    final_phone = user_phone_input.strip()
    
    if final_phone:
        # Извлекаем из строки только чистые цифры
        digits_only = re.sub(r"\D", "", final_phone)
        
        # Если номер начинается с 8 или 7 и в нем 11 цифр (стандартный мобильный РФ)
        if len(digits_only) == 11 and (digits_only.startswith("7") or digits_only.startswith("8")):
            # Откусываем первую цифру и приводим к красивому единому виду +7 (...) ...-..-..
            main_part = digits_only[1:]
            final_phone = f"+7 ({main_part[:3]}) {main_part[3:6]}-{main_part[6:8]}-{main_part[8:10]}"
            st.caption(f"✅ Номер распознан и отформатирован: {final_phone}")
        # Если вставили ровно 10 цифр без семерок/восьмерок
        elif len(digits_only) == 10:
            final_phone = f"+7 ({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:8]}-{digits_only[8:10]}"
            st.caption(f"✅ Номер отформатирован: {final_phone}")
        # Если вставили какой-то другой формат (городской или короткий)
        else:
            st.caption(f"ℹ️ Номер сохранен в исходном виде: {final_phone}")
    else:
        phone_error = "НЕ_ЗАПОЛНЕН"

    st.write("---")
    st.caption("ФОТОФИКСАЦИЯ ВЫДАЧИ (НЕОБЯЗАТЕЛЬНО)")
    photo_person_link = st.text_input("Ссылка на фото получателя", placeholder="https://vk.com...")
    photo_receipt_link = st.text_input("Ссылка на фото расписки", placeholder="https://vk.com...")
    
    # Поля дополнительных и паспортных данных закомментированы, чтобы не загромождать экран
    # (код скрыт с помощью символа #)
    
    st.write("---")
    if st.button("СОХРАНИТЬ ЗАПИСЬ", type="primary", use_container_width=True):
        if not last_name.strip(): st.error("Укажите фамилию")
        elif not first_name.strip(): st.error("Укажите имя")
        elif not middle_name.strip(): st.error("Укажите отчество")
        elif phone_error == "НЕ_ЗАПОЛНЕН": st.error("Укажите номер телефона")
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
                st.success(f"Запись успешно сохранена: {full_fio}")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Ошибка сохранения: в базе уже есть человек с таким ФИО и номером телефона!")

with tab2:
    db_admin.show_admin_panel()
    st.write("---")
    
    if "shelter_records" in st.session_state and not st.session_state.shelter_records.empty:
        mb.render_barnaul_map(st.session_state.shelter_records)
