import streamlit as st
from datetime import date

def show_registration_page():
    # 1. Принудительный строгий шрифт через CSS
    st.markdown("""
        <style>
        html, body, [class*="css"], .stWidgetFormProp, div[data-baseweb="select"] {
            font-family: Arial, Helvetica, sans-serif !important;
        }
        /* Стилизация кнопки сохранения */
        button[data-testid="stBaseButton-secondaryFormSubmit"] {
            border: 2px solid #b1b1b1 !important;
            font-weight: bold !important;
            font-size: 16px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Инициализация памяти для цифр
    if "entered_code" not in st.session_state:
        st.session_state.entered_code = ""

    st.subheader("📝 Форма регистрации и ввода данных")

    # Выносим цифровую панель из формы, чтобы кнопки реагировали мгновенно
    st.write("**Введенный код / Номер:**")
    st.code(st.session_state.entered_code if st.session_state.entered_code else "Нажимайте цифры ниже...", language="text")
    
    # Строгая сеточка обычных кнопок 3х4 (НЕ form_submit_button)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("1", use_container_width=True): st.session_state.entered_code += "1"; st.rerun()
        if st.button("4", use_container_width=True): st.session_state.entered_code += "4"; st.rerun()
        if st.button("7", use_container_width=True): st.session_state.entered_code += "7"; st.rerun()
        if st.button("C (Сброс)", use_container_width=True): st.session_state.entered_code = ""; st.rerun()
    with col2:
        if st.button("2", use_container_width=True): st.session_state.entered_code += "2"; st.rerun()
        if st.button("5", use_container_width=True): st.session_state.entered_code += "5"; st.rerun()
        if st.button("8", use_container_width=True): st.session_state.entered_code += "8"; st.rerun()
        if st.button("0", use_container_width=True): st.session_state.entered_code += "0"; st.rerun()
    with col3:
        if st.button("3", use_container_width=True): st.session_state.entered_code += "3"; st.rerun()
        if st.button("6", use_container_width=True): st.session_state.entered_code += "6"; st.rerun()
        if st.button("9", use_container_width=True): st.session_state.entered_code += "9"; st.rerun()
        if st.button("← (Стереть)", use_container_width=True): st.session_state.entered_code = st.session_state.entered_code[:-1]; st.rerun()

    st.write("---")

    # Форма только для анкетных данных и отправки
    with st.form("digital_panel_form"):
        district = st.selectbox(
            "Район г. Барнаула *",
            options=["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный"],
            index=None,
            placeholder="Выберите район..."
        )
        
        birth_date = st.date_input(
            "Дата рождения *",
            value=date(1995, 1, 1),
            min_value=date(1920, 1, 1),
            max_value=date.today(),
            format="DD.MM.YYYY"
        )
        
        address = st.text_input("Адрес (по желанию)", placeholder="ул. Ленина, д. 10")
        
        # Единственная кнопка отправки формы
        save_btn = st.form_submit_button("🔴 СОХРАНИТЬ ВСЕ ДАННЫЕ", use_container_width=True)
        
        if save_btn:
            if not district:
                st.error("Ошибка: выберите район города!")
            elif not st.session_state.entered_code:
                st.error("Ошибка: код не может быть пустым!")
            else:
                st.success("Данные успешно зафиксированы!")
                return {
                    "code": st.session_state.entered_code,
                    "district": district,
                    "birth_date": birth_date,
                    "address": address
                }
    return None
