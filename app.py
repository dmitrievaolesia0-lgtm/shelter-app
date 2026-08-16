import streamlit as st
import sqlite3
import pandas as pd

from fields import get_user_inputs
from validators import validate_phone

# Инициализация сессии для телефона ДО вызова виджетов
if 'phone_buffer' not in st.session_state:
    st.session_state['phone_buffer'] = "+7"

def init_db():
    conn = sqlite3.connect('shelter_cats.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_delivery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            birth_year TEXT,
            phone TEXT NOT NULL UNIQUE,
            feed_type TEXT NOT NULL,
            delivery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Приют Кошек", page_icon="🐱", layout="wide")
st.title("🐱 Учёт выдачи корма для кошек")
st.subheader("Регистрация выдачи")

# Оборачиваем ввод в форму для изоляции триггеров
with st.form("delivery_registration_form", clear_on_submit=False):
    
    # Функция должна принимать или использовать st.session_state['phone_buffer'] внутри себя как key
    user_data = get_user_inputs()
    
    # Кнопка отправки формы (заменяет обычный st.button)
    submit_btn = st.form_submit_button("💾 ПРОВЕРИТЬ И СОХРАНИТЬ", use_container_width=True)

# Обработка нажатия кнопки формы
if submit_btn:
    if user_data.get('last_name') and user_data.get('first_name') and user_data.get('phone_raw'):
        is_valid, phone_result = validate_phone(user_data['phone_raw'])
        
        if not is_valid:
            st.error(phone_result)
        else:
            try:
                conn = sqlite3.connect('shelter_cats.db')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO food_delivery 
                    (last_name, first_name, middle_name, birth_year, phone, feed_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_data['last_name'], 
                    user_data['first_name'], 
                    user_data['middle_name'], 
                    user_data['birth_year'], 
                    phone_result,
                    user_data['feed_type']
                ))
                conn.commit()
                conn.close()
                
                # Выводим сообщение об успехе глобально
                st.success(f"🎉 Успешно сохранено! Номер: {phone_result}")
                
                # Сбрасываем буфер телефона и принудительно обновляем интерфейс
                st.session_state['phone_buffer'] = "+7"
                st.rerun()
                
            except sqlite3.IntegrityError:
                st.error("⚠️ Ошибка: Человек с таким номером телефона уже есть в базе данных!")
    else:
        st.warning("❗ Заполните обязательные поля: Фамилия, Имя и Телефон.")

st.divider()
st.subheader("📊 База данных")

# Безопасное чтение из БД
try:
    conn = sqlite3.connect('shelter_cats.db')
    df = pd.read_sql_query("SELECT * FROM food_delivery ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        # Настройка отображения таблицы (скрываем технический ID по желанию)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("База пока пуста.")
except Exception as e:
    st.error(f"Ошибка загрузки базы данных: {e}")
