import streamlit as st
from datetime import date

def render_date_picker(label="Дата рождения", key_prefix="birth"):
    """Отрисовывает компонент выбора даты с переключением режимов."""
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
            year = st.selectbox("Год", range(2026, 1900, -1), key=f"{key_prefix}_year")
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
        selected_date = st.date_input(
            "Календарь", 
            value=date(2000, 1, 1), 
            key=f"{key_prefix}_calendar",
            format="DD/MM/YYYY"
        )
        st.success(f"Выбрана дата: {selected_date.strftime('%d.%m.%Y')}")
        
    return selected_date.strftime('%Y-%m-%d')

if __name__ == "__main__":
    st.title("Тест модуля даты")
    res_date = render_date_picker()
    st.write("Дата в формате для БД:", res_date)
