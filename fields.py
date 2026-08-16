import streamlit as st

def get_user_inputs():
    inputs = {}
    
    # Стандартные поля ФИО
    inputs['last_name'] = st.text_input("👤 Фамилия *", placeholder="Иванов")
    inputs['first_name'] = st.text_input("👤 Имя *", placeholder="Иван")
    inputs['middle_name'] = st.text_input("👤 Отчество (необязательно)", placeholder="Сергеевич")
    inputs['birth_year'] = st.text_input("📅 Год рождения (необязательно)", placeholder="1995")
    
    st.write("---")
    st.write("📱 **Виртуальная клавиатура телефона (HTML + Циклы Python):**")
    
    # Инициализируем буфер телефона
    if 'phone_buffer' not in st.session_state:
        st.session_state['phone_buffer'] = "+7"
        
    # Слушатель нажатий кнопок
    if "click" in st.query_params:
        clicked_val = st.query_params["click"]
        if clicked_val == "clear":
            st.session_state['phone_buffer'] = "+7"
        elif clicked_val == "back":
            if len(st.session_state['phone_buffer']) > 2:
                st.session_state['phone_buffer'] = st.session_state['phone_buffer'][:-1]
        else:
            st.session_state['phone_buffer'] += clicked_val
            
        st.query_params.clear()
        st.rerun()

    # Выводим крупно набранный номер
    st.info(f"### 📞 Набрано: {st.session_state['phone_buffer']}")
    
    # ─── МАГИЯ ЦИКЛОВ И МАССИВОВ ───
    # Описываем матрицу телефона в виде структуры данных (список строк)
    # Вместо эмодзи передаем кодовые слова для логики кликов
    phone_layout = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["clear", "0", "back"]
    ]
    
    # Базовые CSS-стили для оформления кнопок
    html_table = """
    <style>
        .phone-table { width: 100%; max-width: 300px; margin: 0 auto; border-collapse: separate; border-spacing: 8px; }
        .phone-cell { width: 33%; text-align: center; background-color: #f0f2f6; border-radius: 8px; padding: 15px 0; font-weight: bold; font-size: 22px; }
        .phone-cell a { color: #31333F !important; text-decoration: none !important; display: block; width: 100%; height: 100%; }
        .phone-cell:active { background-color: #dddfe4; }
        .special-btn { background-color: #ffe0e0; }
    </style>
    <table class="phone-table">
    """
    
    # Запускаем вложенные циклы, чтобы сгенерировать HTML-код без дублирования
    for row in phone_layout:
        html_table += "<tr>"  # Открываем строчку таблицы HTML
        for item in row:
            # Превращаем технические слова в красивые иконки для экрана
            display_text = item
            cell_class = "phone-cell"
            
            if item == "clear":
                display_text = "❌"
                cell_class += " special-btn"
            elif item == "back":
                display_text = "⬅️"
                cell_class += " special-btn"
                
            # Добавляем ячейку в строку таблицы
            html_table += f'<td class="{cell_class}"><a href="/?click={item}">{display_text}</a></td>'
            
        html_table += "</tr>"  # Закрываем строчку таблицы HTML
        
    html_table += "</table>"
    
    # Выводим сгенерированный в цикле HTML-код на экран Streamlit
    st.markdown(html_table, unsafe_allow_html=True)

    inputs['phone_raw'] = st.session_state['phone_buffer']
    inputs['feed_type'] = st.selectbox("📦 Какой корм выдаём?", ["Сухой для кошек", "Влажный для кошек"])
    
    return inputs

