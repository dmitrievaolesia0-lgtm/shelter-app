import streamlit as st
import pandas as pd
from datetime import datetime

def render_birthday_alert(df):
    """Выводит список людей, у которых день рождения в выбранном месяце."""
    st.write("---")
    st.markdown("<small style='color: #7F8C8D; font-weight: bold;'>БЛИЖАЙШИЕ ДНИ РОЖДЕНИЯ</small>", unsafe_allow_html=True)
    
    if df.empty:
        return

    months_ru = {
        1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 
        5: "Май", 6: "Июнь", 7: "Июль", 8: "Август", 
        9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    }
    
    current_month_num = datetime.today().month
    
    selected_month_name = st.selectbox(
        "Показать именинников за месяц:",
        options=list(months_ru.values()),
        index=current_month_num - 1,
        key="birthday_month_selector"
    )
    
    selected_month_num = [k for k, v in months_ru.items() if v == selected_month_name]
    
    birthday_people = []
    
    for _, row in df.iterrows():
        b_date_str = row.get('birth_date', '')
        
        if not b_date_str or pd.isna(b_date_str) or b_date_str in ["Не указана", "Не указан", ""]:
            continue
            
        try:
            b_date = pd.to_datetime(b_date_str).date()
            
            if b_date.month == selected_month_num:
                today = datetime.today().date()
                age = today.year - b_date.year
                
                birthday_people.append({
                    "fio": row.get('fio', 'Без имени'),
                    "day": b_date.day,
                    "age": age,
                    "phone": row.get('phone', '-')
                })
        except:
            continue
            
    if birthday_people:
        birthday_people = sorted(birthday_people, key=lambda x: x['day'])
        
        for person in birthday_people:
            st.markdown(
                f"<div style='font-size: 14px; color: #2C3E50; margin-bottom: 4px;'>"
                f"<b>{person['day']:02d} числа</b> — {person['fio']} (исполняется: {person['age']}) | Тел: {person['phone']}"
                f"</div>", 
                unsafe_allow_html=True
            )
    else:
        st.markdown("<small style='color: #95A5A6; font-style: italic;'>В этом месяце дней рождения не найдено.</small>", unsafe_allow_html=True)
