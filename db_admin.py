import streamlit as st
import part_1_prepare_data as p1
import part_2_filter_data as p2
import part_3_render_view as p3
import db_analytics as analytics

def show_admin_panel():
    """Главный пульт управления архивом и аналитикой"""
    
    # Шаг 1: Загрузка и первичная подготовка данных
    df, sort_options, selected_sort, selected_districts, view_mode = p1.part_1_prepare_data()
    
    # Если база данных пуста — останавливаем выполнение
    if df is None:
        return

    # Шаг 2: Фильтрация данных по критериям поиска оператора
    filtered_df, display_df = p2.part_2_filter_data(df, sort_options, selected_sort, selected_districts)

    # Шаг 3: Вывод карточек или компактной интерактивной таблицы
    p3.part_3_render_view(view_mode, filtered_df, display_df, df)
    
    # Шаг 4: Вывод строгого блока аналитики (статистика по районам Барнаула)
    analytics.show_analytics_panel(display_df)
