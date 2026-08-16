import streamlit as st

def get_user_inputs():
    inputs = {}
    
    inputs['last_name'] = st.text_input("👤 Фамилия *", placeholder="Иванов")
    inputs['first_name'] = st.text_input("👤 Имя *", placeholder="Иван")
    inputs['middle_name'] = st.text_input("👤 Отчество (необязательно)", placeholder="Сергеевич")
    inputs['birth_year'] = st.text_input("📅 Год рождения (необязательно)", placeholder="1995")
    
    st.write("---")
    st.write("📱 **Виртуальная клавиатура телефона:**")
    
    if 'phone_buffer' not in st.session_state:
        st.session_state['phone_buffer'] = "+7"
        
    st.info(f"### 📞 Набрано: {st.session_state['phone_buffer']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("1", use_container_width=True): st.session_state['phone_buffer'] += "1"
    with col2:
        if st.button("2", use_container_width=True): st.session_state['phone_buffer'] += "2"
    with col3:
        if st.button("3", use_container_width=True): st.session_state['phone_buffer'] += "3"
        
    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button("4", use_container_width=True): st.session_state['phone_buffer'] += "4"
    with col5:
        if st.button("5", use_container_width=True): st.session_state['phone_buffer'] += "5"
    with col6:
        if st.button("6", use_container_width=True): st.session_state['phone_buffer'] += "6"
        
    col7, col8, col9 = st.columns(3)
    with col7:
        if st.button("7", use_container_width=True): st.session_state['phone_buffer'] += "7"
    with col8:
        if st.button("8", use_container_width=True): st.session_state['phone_buffer'] += "8"
    with col9:
        if st.button("9", use_container_width=True): st.session_state['phone_buffer'] += "9"
        
    col_clear, col0, col_back = st.columns(3)
    with col_clear:
        if st.button("❌ Сброс", use_container_width=True): 
            st.session_state['phone_buffer'] = "+7"
    with col0:
        if st.button("0", use_container_width=True): st.session_state['phone_buffer'] += "0"
    with col_back:
        if st.button("⬅️ Стереть", use_container_width=True):
            if len(st.session_state['phone_buffer']) > 2:
                st.session_state['phone_buffer'] = st.session_state['phone_buffer'][:-1]

    inputs['phone_raw'] = st.session_state['phone_buffer']
    
    # Выбор кошачьего корма
    inputs['feed_type'] = st.selectbox("📦 Какой корм выдаём?", ["Сухой для кошек", "Влажный для кошек"])
    
    return inputs
