import streamlit as st

def get_user_inputs():
    # ИСПРАВЛЕНО: убрана лишняя буква 'd' в слове allow
    st.markdown("""
        <style>
        html, body, [class*="css"], .stWidgetFormProp {
            font-family: Arial, Helvetica, sans-serif !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Примерная структура ваших полей (проверьте соответствие вашим полям)
    last_name = st.text_input("Фамилия *")
    first_name = st.text_input("Имя *")
    middle_name = st.text_input("Отчество (по желанию)")
    birth_year = st.text_input("Год рождения")
    
    # Сверяем с ключом phone_buffer, о котором говорили ранее
    phone_raw = st.text_input("Телефон *", key="phone_buffer")
    
    feed_type = st.selectbox("Тип корма *", options=["Сухой", "Влажный", "Лечебный"])

    # Функция ОБЯЗАТЕЛЬНО должна возвращать словарь со всеми ключами
    return {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name,
        "birth_year": birth_year,
        "phone_raw": phone_raw,
        "feed_type": feed_type
    }
