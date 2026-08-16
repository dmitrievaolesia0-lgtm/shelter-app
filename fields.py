import streamlit as st
from datetime import date

# 1. СТРОГИЙ СТИЛЬ (Шрифты и оформление сеточки кнопок)
st.markdown("""
    <style>
    /* Установка строгого шрифта для всего приложения */
    html, body, [class*="css"], .stWidgetFormProp {
        font-family: Arial, Helvetica, sans-serif !important;
    }
    
    /* Контейнер для цифровой сеточки */
    .number-grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        background-color: #f0f2f6;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #dcdfe6;
        margin-bottom: 20px;
    }
    
    /* Стиль строгих кнопок-ячеек в сетке */
    .grid-btn {
        background-color: #ffffff;
        color: #222222;
        border: 2px solid #cbd5e1;
        border-radius: 6px;
        padding: 15px 0;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        transition: all 0.15s ease;
    }
    .grid-btn:hover {
        background-color: #f8fafc;
        border-color: #94a3b8;
    }
    </style>
""", unsafe_allow_html=True)

# 2. ИНИЦИАЛИЗАЦИЯ ПАМЯТИ (Чтобы цифры не стирались при перезапуске)
if "entered_code" not in st.session_state:
    st.session_state.entered_code = ""

st.title("📋 Регистрация и ввод данных")

# Создаем форму, чтобы страница не обновлялась хаотично при каждом клике
with st.form("main_registration_form"):
    
    # Поле вывода кода (только для чтения, данные берутся из session_state)
    st.write("**Введенный код / Номер:**")
    st.code(st.session_state.entered_code if st.session_state.entered_code else "Нажимайте цифры ниже...", language="text")
    
    # Визуальная сеточка цифр (используем колонки Streamlit для создания сетки)
    # Кнопки внутри st.form сработают как нужно, но чтобы точнее управлять вводом,
    # мы выводим их в строгую сетку 3х4
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.form_submit_button("1", use_container_width=True): st.session_state.entered_code += "1"; st.rerun()
        if st.form_submit_button("4", use_container_width=True): st.session_state.entered_code += "4"; st.rerun()
        if st.form_submit_button("7", use_container_width=True): st.session_state.entered_code += "7"; st.rerun()
        if st.form_submit_button("Сброс (C)", use_container_width=True): st.session_state.entered_code = ""; st.rerun()
        
    with col2:
        if st.form_submit_button("2", use_container_width=True): st.session_state.entered_code += "2"; st.rerun()
        if st.form_submit_button("5", use_container_width=True): st.session_state.entered_code += "5"; st.rerun()
        if st.form_submit_button("8", use_container_width=True): st.session_state.entered_code += "8"; st.rerun()
        if st.form_submit_button("0", use_container_width=True): st.session_state.entered_code += "0"; st.rerun()
        
    with col3:
        if st.form_submit_button("3", use_container_width=True): st.session_state.entered_code += "3"; st.rerun()
        if st.form_submit_button("6", use_container_width=True): st.session_state.entered_code += "6"; st.rerun()
        if st.form_submit_button("9", use_container_width=True): st.session_state.entered_code += "9"; st.rerun()
        if st.form_submit_button(" Стереть (←) ", use_container_width=True): st.session_state.entered_code = st.session_state.entered_code[:-1]; st.rerun()

    st.write("---") # Разделительная линия

    # 3. ДОБАВЛЕННЫЕ ПОЛЯ (Район, Дата рождения, Адрес)
    
    # Обязательный выбор района Барнаула
    district = st.selectbox(
        "Район г. Барнаула *",
        options=["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный"],
        index=None,
        placeholder="Выберите район из списка..."
    )
    
    # Дата рождения (встроенный выбор: день, месяц, год)
    birth_date = st.date_input(
        "Дата рождения *",
        value=date(1995, 1, 1), # Начальное значение по умолчанию
        min_value=date(1920, 1, 1),
        max_value=date.today(),
        format="DD.MM.YYYY"
    )
    
    # Необязательный адрес
    address = st.text_input(
        "Адрес (по желанию)", 
        placeholder="Например: ул. Ленина, д. 15, кв. 4"
    )
    
    # Главная кнопка отправки всей формы
    submit_button = st.form_submit_button("СОХРАНИТЬ ВСЕ ДАННЫЕ")
    
    if submit_button:
        # Проверка заполнения обязательных полей
        if not district:
            st.error("Пожалуйста, обязательно выберите район города!")
        elif not st.session_state.entered_code:
            st.error("Пожалуйста, введите код с помощью цифровой панели!")
        else:
            st.success("Данные успешно приняты и сохранены!")
            # Здесь вы можете прописать логику связи с другими вашими файлами:
            # Например: save_to_database(st.session_state.entered_code, district, birth_date, address)

