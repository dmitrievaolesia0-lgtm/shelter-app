import streamlit as st
import pandas as pd
from datetime import date
import db_core as core

def part_1_prepare_data():
    """Часть 1: Инициализация данных и подготовка критериев сортировки/фильтрации"""
    st.caption("АРХИВ И АНАЛИТИКА (ОБЛАКО ЯНДЕКС)")
    
    if st.button("🔄 Обновить данные из облака", use_container_width=True):
        core.clear_db_cache()
        st.rerun()
        
    df = core.cached_download()
        
    if df.empty or len(df) == 0:
        st.write("---")
        st.info("Архив базы данных пуст.")
        return None, None, None, None, None

    # Понятные и строгие критерии сортировки для оператора
    sort_options = {
        "По дате визита (сначала новые)": ("visit_date", False),
        "По дате визита (сначала старые)": ("visit_date", True),
        "По алфавиту (ФИО: А-Я)": ("fio", True),
    }
    
    col1, col2 = st.columns(2)
    with col1:
        selected_sort = st.selectbox("Сортировка списка жителей", list(sort_options.keys()))
    with col2:
        view_mode = st.radio(
            "Формат вывода карточек:",
            ["Полная анкета (Карточки)", "Компактный вид (Строки)"],
            horizontal=True
        )

    # Мультивыбор районов (можно выбрать один, несколько или смотреть все)
    all_barnaul_districts = ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]
    selected_districts = st.multiselect("Фильтр по административным районам", options=all_barnaul_districts, default=[])
    
    return df, sort_options, selected_sort, selected_districts, view_mode
