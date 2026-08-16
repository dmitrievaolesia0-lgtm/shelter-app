import streamlit as st
import sqlite3
import pandas as pd

# Настройка базы данных SQL
def init_db():
    conn = sqlite3.connect('shelter_data.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_delivery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            feed_type TEXT NOT NULL,
            delivery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Создаем красивый интерфейс
st.set_page_config(page_title="Приют Учёт", page_icon="🐾")
st.title("🐾 Система учёта приюта")
st.subheader("Форма регистрации выдачи корма")

# Поля ввода для волонтёра
name = st.text_input("👤 Имя и Фамилия получателя", placeholder="Например: Иван Петров")
phone = st.text_input("📱 Номер телефона", placeholder="Только цифры, например: 79991112233")
feed = st.selectbox("📦 Какой корм выдаём?", ["Сухой для собак", "Влажный для кошек", "Гипоаллергенный"])

if st.button("💾 СОХРАНИТЬ В БАЗУ ДАННЫХ", use_container_width=True):
    if name and phone:
        try:
            conn = sqlite3.connect('shelter_data.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO food_delivery (client_name, phone, feed_type) VALUES (?, ?, ?)", 
                (name, phone, feed)
            )
            conn.commit()
            conn.close()
            st.success(f"🎉 Данные успешно записаны в SQL! Добавлен: {name}")
        except sqlite3.IntegrityError:
            st.error("⚠️ Ошибка: Человек с таким номером телефона уже есть в базе данных!")
    else:
        st.warning("❗ Пожалуйста, заполните обязательные поля: Имя и Телефон.")

# Блок просмотра данных для администратора
st.divider()
st.subheader("📊 Текущая база (для проверки)")
conn = sqlite3.connect('shelter_data.db')
df = pd.read_sql_query("SELECT * FROM food_delivery", conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("База данных пока пуста. Внесите первую запись выше!")
