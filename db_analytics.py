import streamlit as st
import pandas as pd

def show_analytics_panel(df):
    """Модуль аналитики: Вывод строгого распределения жителей по районам города"""
    if df.empty:
        st.info("Нет данных для построения аналитических отчетов.")
        return

    st.write("---")
    st.caption("СТАТИСТИКА РАСПРЕДЕЛЕНИЯ ДАННЫХ ПО РАЙОНАМ")
    
    # Подсчет количества записей по каждому административному району
    if 'district' in df.columns:
        district_counts = df['district'].value_counts().reset_index()
        district_counts.columns = ['Административный район', 'Количество жителей']
        
        # Строгий вывод данных в виде компактной таблицы
        st.dataframe(district_counts, use_container_width=True, hide_index=True)
    else:
        st.caption("Данные по административным районам отсутствуют.")

def make_phone_callable(phone_str):
    """Вспомогательная функция для создания кликабельной ссылки на номер телефона"""
    clean_phone = str(phone_str).replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
    return f'<a href="tel:{clean_phone}" style="color: #111111; text-decoration: underline;">{phone_str}</a>'

def calculate_age(birth_date_val):
    """Техническая функция-заглушка. Предотвращает ошибки в других файлах системы."""
    return 999
