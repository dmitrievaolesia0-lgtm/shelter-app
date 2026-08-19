import streamlit as st
import pandas as pd

import part_1_prepare_data as p1
import part_2_filter_data as p2
import part_3_render_view as p3

def show_admin_panel():
    """Главная управляющая функция админ-панели, связывающая все части воедино."""
    
    # Часть 1: Подготовка данных, сортировка и выбор режима отображения
    res_p1 = p1.part_1_prepare_data()
    if res_p1[0] is None:
        return
        
    df, sort_options, selected_sort, selected_districts, view_mode = res_p1
    
    # Часть 2: Поиск, фильтрация по районам/датам и пагинация
    filtered_df, display_df = p2.part_2_filter_data(
        df, sort_options, selected_sort, selected_districts
    )
    
    # Часть 3: Рендеринг списка (передаем строго 2 аргумента, как объявлено в модуле p3)
    p3.part_3_render_view(filtered_df, df)
