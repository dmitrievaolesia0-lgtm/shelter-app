import streamlit as st
import pandas as pd
from datetime import date, datetime

import yandex_cloud as cloud
import db_core as core
import db_dialogs as dialogs
import db_analytics as analytics
import db_birthdays as birthdays

# Перенаправляем функции для совместимости с главным файлом app.py
init_db = core.init_db
add_recipient = core.add_recipient

def show_admin_panel():
    st.caption("АРХИВ И АНАЛИТИКА (ОБЛАКО ЯНДЕКС)")
    
    # Кнопка мгновенно сбрасывает кэш и скачивает свежий файл
    if st.button("🔄 Обновить данные из облака", use_container_width=True):
        core.clear_db_cache()
        st.rerun()
        
    # Данные берутся из быстрого кэша оперативной памяти
    df = core.cached_download()
        
    if df.empty or len(df) == 0:
        st.write("---")
        st.info("Архив базы данных пуст.")
        return

    # 1. СОРТИРОВКА И РАЙОНЫ (ИСПРАВЛЕНО: убрана сортировка по районам)
    sort_options = {
        "Сначала новые визиты": ("visit_date", False),
        "Сначала старые визиты": ("visit_date", True),
        "От старших к младшим (Возраст)": ("Возраст", True),
        "По алфавиту (ФИО)": ("fio", True)
    }
    selected_sort = st.selectbox("Сортировка списка", list(sort_options.keys()))

    all_barnaul_districts = ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]
    selected_districts = st.multiselect("Фильтр по районам города (Оставьте пустым для показа ВСЕЙ базы)", options=all_barnaul_districts, default=[])

    # НАСТРОЙКА ВИДА ВЫВОДА (ИСПРАВЛЕНО: текст переключателя изменен)
    view_mode = st.radio(
        "Формат вывода данных:",
        ["Полная анкета (Карточки)", "Компактный вид (ФИО + Телефон + Район + Дата)"],
        horizontal=True
    )

    st.write("---")
    
    # 2. РАЗДЕЛЬНЫЙ ПОИСК
    col1, col2 = st.columns(2)
    with col1:
        search_fio = st.text_input("Поиск по ФИО (можно ввести что-то одно)", placeholder="Гридин или Иван...")

    with col2:
        search_phone = st.text_input("Поиск по номеру телефона", placeholder="999...")

    # 3. АКТИВАЦИЯ ПЕРИОДА ПОСЕЩЕНИЯ
    st.write("---")
    use_date_filter = st.checkbox("🔄 Фильтровать по периоду посещения", value=False)
    
    if 'visit_date' in df.columns:
        df['visit_date_parsed'] = pd.to_datetime(df['visit_date'], errors='coerce').dt.date
        min_date, max_value = df['visit_date_parsed'].min(), df['visit_date_parsed'].max()
        if pd.isna(min_date): min_date = date.today()
        if pd.isna(max_value): max_value = date.today()
    else:
        min_date, max_value = date.today(), date.today()

    if min_date > max_value: min_date = max_value
    
    date_range = st.date_input(
        "Период посещения", 
        value=(min_date, max_value), 
        min_value=min_date, 
        max_value=max_value,
        disabled=not use_date_filter
    )

    # Расчет колонок перед фильтрацией
    df['Возраст'] = df['birth_date'].apply(core.calculate_age)
    df['День недели визита'] = df['visit_date'].apply(core.get_weekday_name)

    # Применение фильтров
    filtered_df = df.copy()
    
    if search_fio:
    filtered_df = filtered_df[filtered_df['fio'].astype(str).str.contains(search_fio, case=False, na=False)]

        
    if search_phone:
        filtered_df = filtered_df[filtered_df['phone'].astype(str).str.contains(search_phone, na=False)]
    
    if selected_districts:
        filtered_df = filtered_df[filtered_df['district'].isin(selected_districts)]
        
    if use_date_filter and isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['visit_date_parsed'] >= start_date) & (filtered_df['visit_date_parsed'] <= end_date)]

    # Сортировка
    sort_column, ascending_order = sort_options[selected_sort]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending_order)
    
    if 'visit_date_parsed' in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=['visit_date_parsed'])
        
    display_df = filtered_df.copy()
    display_df['Возраст'] = display_df['Возраст'].apply(lambda x: "Не указан" if x == 999 else x)
    st.session_state.shelter_records = display_df

    st.write("---")
    st.caption(f"НАЙДЕНО ЗАПИСЕЙ В БАЗЕ: {len(display_df)}")

    # Отображение данных (ИСПРАВЛЕНО: обновлен текст условия соответствия радиокнопке)
    if view_mode == "Компактный вид (ФИО + Телефон + Район + Дата)":
        short_df = display_df[['fio', 'phone', 'district', 'visit_date']].copy()
        short_df.columns = ['ФИО Получателя', 'Номер телефона', 'Район города', 'Дата визита']
        st.dataframe(short_df, use_container_width=True, hide_index=True)
    else:
        for idx, row in filtered_df.iterrows():
            current_district = row.get('district', 'Не определен')
            if not current_district or pd.isna(current_district):
                current_district = "Не определен"
                
            with st.expander(f"👤 {row.get('fio', 'Без имени')} | [{current_district}]"):
                # 1. КОНТАКТЫ (Кликабельный номер)
                callable_phone = analytics.make_phone_callable(row.get('phone', '-'))
                st.markdown(f"**Контакты:** {callable_phone}", unsafe_allow_html=True)

                # 2. ДАТА ВИЗИТА
                st.markdown(f"**Дата визита:** {row.get('visit_date', '-')} ({row.get('День недели визита', '-')})")
                
                # 3. ССЫЛКИ НА ФОТООТЧЕТ
                photo_str = row.get('photo_path', '')
                photo_person = "Не указана"
                photo_receipt = "Не указана"
                
                if photo_str and "|" in str(photo_str):
                    try:
                        parts = str(photo_str).split("|")
                        for part in parts:
                            if "Человек:" in part:
                                photo_person = part.replace("Человек:", "").strip()
                            if "Расписка:" in part:
                                photo_receipt = part.replace("Расписка:", "").strip()
                    except:
                        pass
                
                links_html = []
                if photo_person and photo_person != "Не указана" and photo_person.startswith("http"):
                    links_html.append(f'<a href="{photo_person}" target="_blank" style="color: #2C3E50; font-weight: bold; text-decoration: underline;">Фото получателя</a>')
                if photo_receipt and photo_receipt != "Не указана" and photo_receipt.startswith("http"):
                    links_html.append(f'<a href="{photo_receipt}" target="_blank" style="color: #2C3E50; font-weight: bold; text-decoration: underline;">Фото расписки</a>')
                
                if links_html:
                    st.markdown(f"**Фотоотчет:** {' | '.join(links_html)}", unsafe_allow_html=True)
                else:
                    st.markdown("**Фотоотчет:** Не прикреплен")
                
                st.write("---")
                st.caption("ПОЛНАЯ АНКЕТА ПОЛУЧАТЕЛЯ")
                
                # 4. ОСТАЛЬНЫЕ ДАННЫЕ АНКЕТЫ
                st.text(f"Возраст: {row.get('Возраст')} (д.р. {row.get('birth_date', '-')})")
                st.text(f"Район проживания: {current_district}")
                st.text(f"Адрес: {row.get('address', '-')}")
                st.text(f"Выданный корм: {row.get('feed_type', '-')}")
                st.text(f"Паспорт: {row.get('passport_series', '-')} {row.get('passport_number', '-')}")
                
                st.write("---")
                # Кнопки управления анкетой
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✏️ Редактировать", key=f"edit_{idx}", use_container_width=True):
                        dialogs.edit_dialog(idx, row, df)
                        core.clear_db_cache()
                with btn_col2:
                    if st.button("🚨 Удалить", key=f"del_{idx}", use_container_width=True):
                        dialogs.delete_dialog(idx, row.get('fio', 'Без имени'), df)
                        core.clear_db_cache()

    # Схематичные графики
    analytics.render_analytics_charts(display_df)
    
    # Блок дней рождения
    birthdays.render_birthday_alert(df)
