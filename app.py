import streamlit as st
import pandas as pd
import re
from datetime import datetime, date

import database as db
import date_picker as dp
import map_barnaul as mb

st.set_page_config(page_title="Учет выдачи корма", layout="centered")
db.init_db()

st.subheader("Регистрация и учет выдачи корма")

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
    
    phone_mode = st.radio(
        "Формат номера:",
        ["Мобильный РФ (+7)", "Иной формат (городской / СНГ)"],
        horizontal=True
    )
    
    if phone_mode == "Мобильный РФ (+7)":
        raw_phone = st.text_input(
            "10 цифр номера (после +7) *", 
            placeholder="9991234567",
            max_chars=10
        )
        digits_only = re.sub(r"\D", "", raw_phone)
        
        if len(digits_only) == 10:
            final_phone = f"+7 ({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:8]}-{digits_only[8:10]}"
            st.caption(f"Сформирован номер: {final_phone}")
            phone_error = None
        elif len(digits_only) > 0:
            st.caption(f"Введено цифр: {len(digits_only)} из 10")
            phone_error = "ОШИБКА_ДЛИНЫ"
            final_phone = ""
        else:
            phone_error = "НЕ_ЗАПОЛНЕН"
            final_phone = ""
    else:
        custom_phone = st.text_input(
            "Номер телефона в произвольном формате *", 
            placeholder="+7 (3852) 12-34-56"
        )
        if custom_phone.strip():
            final_phone = custom_phone.strip()
            phone_error = None
        else:
            phone_error = "НЕ_ЗАПОЛНЕН"
            final_phone = ""

    st.write("---")
    # ИСПРАВЛЕНО: Убраны символы '*' из заголовков, так как поля стали необязательными
    st.caption("ФОТОФИКСАЦИЯ ВЫДАЧИ (НЕОБЯЗАТЕЛЬНО)")
    photo_person_link = st.text_input("Ссылка на фото получателя", placeholder="https://vk.com...")
    photo_receipt_link = st.text_input("Ссылка на фото расписки", placeholder="https://vk.com...")
    
    st.write("---")
    st.caption("ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ (НЕОБЯЗАТЕЛЬНО)")
    
    address = st.text_input("Адрес проживания (Улица, дом, кв.)")
    vk_link = st.text_input("Личная страница получателя (ВК)")
    feed_type = st.text_input("Номенклатура выданного корма")
    
    st.write("---")
    st.caption("ПАСПОРТНЫЕ ДАННЫЕ (НЕОБЯЗАТЕЛЬНО)")
    p_series = st.text_input("Серия паспорта", max_chars=4, placeholder="0000")
    p_number = st.text_input("Номер паспорта", max_chars=6, placeholder="000000")
    p_date = st.text_input("Дата выдачи паспорта", placeholder="ДД.ММ.ГГГГ")
    p_code = st.text_input("Код подразделения", max_chars=7, placeholder="000-000")
    
    birth_date_str = dp.render_date_picker(label="Дата рождения", key_prefix="main_birth")
    
    st.write("---")
    if st.button("СОХРАНИТЬ ЗАПИСЬ", type="primary", use_container_width=True):
        if not last_name.strip(): st.error("Укажите фамилию")
        elif not first_name.strip(): st.error("Укажите имя")
        elif not middle_name.strip(): st.error("Укажите отчество")
        elif phone_error == "НЕ_ЗАПОЛНЕН": st.error("Укажите номер телефона")
        elif phone_error == "ОШИБКА_ДЛИНЫ": st.error("Длина стандартного номера должна составлять 10 цифр")
        # ИСПРАВЛЕНО: Полностью удалены блокировки "if not photo_person_link" и "if not photo_receipt_link"
        else:
            full_fio = f"{last_name.strip()} {first_name.strip()} {middle_name.strip()}"
            final_series = p_series.strip() if p_series.strip() else "0000"
            final_number = p_number.strip() if p_number.strip() else f"б/н-{int(datetime.timestamp(datetime.now()))}"
            visit_date_str = visit_date_selected.strftime('%Y-%m-%d')
            
            # ИСПРАВЛЕНО: Безопасное формирование строки с фото, даже если они не заполнены
            p_link = photo_person_link.strip() if photo_person_link.strip() else "Не указана"
            r_link = photo_receipt_link.strip() if photo_receipt_link.strip() else "Не указана"
            combined_photos = f"Человек: {p_link} | Расписка: {r_link}"
            
            new_record = {
                "fio": full_fio, "birth_date": birth_date_str if birth_date_str else "Не указана",
                "passport_series": final_series, "passport_number": final_number,
                "passport_date": p_date.strip() if p_date.strip() else "Не указана",
                "passport_code": p_code.strip() if p_code.strip() else "Не указан",
                "phone": final_phone, "district": district,
                "vk_link": vk_link.strip() if vk_link.strip() else "Не указана",
                "address": address.strip() if address.strip() else "Не указан",
                "feed_type": feed_type.strip() if feed_type.strip() else "Не указан",
                "photo_path": combined_photos, "visit_date": visit_date_str
            }
            
            success = db.add_recipient(new_record)
            if success:
                st.success(f"Запись успешно сохранена: {full_fio}")
                st.rerun()
            else:
                st.error("Ошибка сохранения: в базе уже есть человек с таким ФИО и номером телефона!")

with tab2:
    db.show_admin_panel()
    st.write("---")
    
    # Подгружаем районы из внутренней памяти для интерактивной карты
    if "shelter_records" in st.session_state and not st.session_state.shelter_records.empty:
        mb.render_barnaul_map(st.session_state.shelter_records)
