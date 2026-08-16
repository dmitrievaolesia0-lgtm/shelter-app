import streamlit as st
from datetime import date

def render_date_picker(label="Дата рождения", key_prefix="birth"):
    """Минималистичный выбор даты рождения в строгом корпоративном стиле."""
    # Строгое отображение без лишних радиокнопок и эмодзи
    selected_date = st.date_input(
        label, 
        value=date(1990, 1, 1),        # Нейтральный год по умолчанию
        min_value=date(1930, 1, 1),    # Нижняя граница возраста
        max_value=date(2026, 12, 31),  # Верхняя граница (текущий год)
        key=f"{key_prefix}_calendar",
        format="DD.MM.YYYY"            # Привычный формат отображения на экране
    )
    
    # Возвращаем строковое представление в формате ГГГГ-ММ-ДД для базы данных
    return selected_date.strftime('%Y-%m-%d')

if __name__ == "__main__":
    st.title("Тест модуля даты")
    res_date = render_date_picker()
    st.write("Результат:", res_date)
