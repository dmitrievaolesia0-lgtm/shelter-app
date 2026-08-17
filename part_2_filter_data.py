import streamlit as st
import pandas as pd
from datetime import date
import db_core as core

def part_2_filter_data(df, sort_options, selected_sort, selected_districts):
    """Часть 2: Поиск, фильтрация по датам/районам и умная постраничная навигация"""
    
    # Расчет параметров «на лету» без дублирования таблиц в памяти
    df['Возраст'] = df['birth_date'].apply(core.calculate_age)
    df['День недели визита'] = df['visit_date'].apply(core.get_weekday_name)

    # Текстовый поиск по ФИО и Контактам
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        search_fio = st.text_input("Поиск по фамилии / имени", placeholder="Ведите текст...", key="search_fio_v4_strict")
    with col2:
        search_phone = st.text_input("Поиск по цифрам телефона", placeholder="999...", key="search_phone_v4_strict")

    # Умный фильтр по календарным периодам визитов
    st.write("---")
    use_date_filter = st.checkbox("Выбрать конкретный период посещения (определенные дни)", value=False)
    
    if 'visit_date' in df.columns:
        df['visit_date_parsed'] = pd.to_datetime(df['visit_date'], errors='coerce').dt.date
        min_date, max_value = df['visit_date_parsed'].min(), df['visit_date_parsed'].max()
        if pd.isna(min_date): min_date = date.today()
        if pd.isna(max_value): max_value = date.today()
    else:
        min_date, max_value = date.today(), date.today()

    if min_date > max_value: min_date = max_value
    
    date_range = st.date_input(
        "Укажите диапазон дат (например: с 5 по 10 число)", 
        value=(min_date, max_value), 
        min_value=min_date, 
        max_value=max_value,
        disabled=not use_date_filter
    )

    # ПРИМЕНЕНИЕ КРИТЕРИЕВ ОТБОРА (Прямая фильтрация в памяти)
    filtered_df = df
    
    if search_fio:
        filtered_df = filtered_df[filtered_df['fio'].astype(str).str.contains(search_fio, case=False, na=False)]
    if search_phone:
        filtered_df = filtered_df[filtered_df['phone'].astype(str).str.contains(search_phone, na=False)]
    if selected_districts:
        filtered_df = filtered_df[filtered_df['district'].isin(selected_districts)]
        
    # Обработка выбора дат (фильтр по диапазону или по одной дате)
    if use_date_filter:
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[(filtered_df['visit_date_parsed'] >= start_date) & (filtered_df['visit_date_parsed'] <= end_date)]
        elif isinstance(date_range, date):
            filtered_df = filtered_df[filtered_df['visit_date_parsed'] == date_range]

    # Сортировка данных перед выводом
    sort_column, ascending_order = sort_options[selected_sort]
    filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending_order)
    
    if 'visit_date_parsed' in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=['visit_date_parsed'])
        
    display_df = filtered_df
    st.session_state.shelter_records = display_df

    total_records = len(display_df)

    # Вывод счетчика найденных строк
    st.write("---")
    st.markdown(f"**Найдено записей в базе:** {total_records}")
    st.write("---")
    
    # НАВИГАЦИЯ ПО СТРАНИЦАМ (Включается только если записей больше 15)
    limit_per_page = 15
    
    if total_records > limit_per_page:
        total_pages = (total_records + limit_per_page - 1) // limit_per_page
        
        if "current_page_num" not in st.session_state:
            st.session_state.current_page_num = 1
            
        page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
        with page_col1:
            if st.button("⬅️ Назад", disabled=st.session_state.current_page_num == 1, use_container_width=True):
                st.session_state.current_page_num -= 1
                st.rerun()
        with page_col2:
            st.markdown(f"<p style='text-align: center; margin-top: 5px; color: #666;'>Страница {st.session_state.current_page_num} из {total_pages}</p>", unsafe_allow_html=True)
        with page_col3:
            if st.button("Вперед ➡️", disabled=st.session_state.current_page_num == total_pages, use_container_width=True):
                st.session_state.current_page_num += 1
                st.rerun()
                
        # Нарезаем массив строк для вывода текущей страницы
        start_idx = (st.session_state.current_page_num - 1) * limit_per_page
        end_idx = start_idx + limit_per_page
        filtered_df = filtered_df.iloc[start_idx:end_idx]
    else:
        # Если записей мало (меньше 15) — показываем их все сразу, кнопки навигации не выводятся
        st.session_state.current_page_num = 1

    return filtered_df, display_df
