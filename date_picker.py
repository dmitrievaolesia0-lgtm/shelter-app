import streamlit as st
from datetime import date

def render_date_picker(label="Дата рождения", key_prefix="birth"):
    """Отрисовывает компонент выбора даты с расширенным диапазоном лет (от 1930 до 2026)."""
    st.subheader(f"📅 {label}")
    
    mode = st.radio(
        "Способ ввода", 
        ["Пошаговый (Год/Месяц/День)", "Календарь"], 
        key=f"{key_prefix}_mode",
        horizontal=True
    )
    
    selected_date = None
    
    if mode == "Пошаговый (Год/Месяц/День)":
        col1, col2, col3 = st.columns(3)
        with col1:
            # Расширили диапазон: от 2026 года назад до 1930 года
            year = st.selectbox("Год", range(2026, 1929, -1), key=f"{key_prefix}_year")
        with col2:
            month = st.selectbox("Месяц", range(1, 13), key=f"{key_prefix}_month")
        with col3:
            day = st.selectbox("День", range(1, 32), key=f"{key_prefix}_day")
            
        try:
            selected_date = date(year, month, day)
            st.success(f"Выбрана дата: {selected_date.strftime('%d.%m.%Y')}")
        except ValueError:
            st.error("Такой даты не существует в выбранном месяце (например, 31 февраля).")
    else:
        # Для стандартного календаря также расширяем границы выбора
        selected_date = st.date_input(
            "Календарь", 
            value=date(1980, 1, 1), # Начальное значение по умолчанию сдвинули на 1980
            min_value=date(1930, 1, 1), # Минимальный доступный год
            max_value=date(2026, 12, 31), # Максимальный доступный год
            key=f"{key_prefix}_calendar",
            format="DD/MM/YYYY"
        )
        st.success(f"Выбрана дата: {selected_date.strftime('%d.%m.%Y')}")
        
    return selected_date.strftime('%Y-%m-%d')

if __name__ == "__main__":
    st.title("Тест модуля даты")
    res_date = render_date_picker()
    st.write("Дата в формате для БД:", res_date)
