import streamlit as st
import pandas as pd

def show_analytics_panel(df):
    """Модуль аналитики: Безопасный и строгий вывод жителей по районам города"""
    if df.empty:
        st.info("Нет данных для построения отчетов.")
        return

    st.write("---")
    st.caption("СПИСКИ ЖИТЕЛЕЙ ПО АДМИНИСТРАТИВНЫМ РАЙОНАМ")
    
    # Полный список районов Барнаула
    all_districts = ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]

    # Перебираем каждый район по очереди
    for district in all_districts:
        district_df = df[df['district'] == district]
        count_in_district = len(district_df)
        
        # Строгий текстовый заголовок без эмодзи
        district_header = f"Район: {district} (Записей: {count_in_district})"
        
        with st.expander(district_header, expanded=False):
            if district_df.empty:
                st.caption("В данном районе зарегистрированных записей не найдено.")
            else:
                # Выводим жителей района с помощью стандартных инструментов Streamlit
                for idx, row in district_df.iterrows():
                    fio_text = row.get('fio', 'Без имени')
                    phone_val = row.get('phone', '-')
                    
                    # Очищаем телефон для создания безопасной ссылки для звонка
                    clean_phone = str(phone_val).replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
                    
                    # 1. Сверху выводим ФИО стандартным текстом
                    st.text(fio_text)
                    
                    # 2. Снизу под ФИО выводим кликабельный телефон с трубкой в виде чистой ссылки
                    st.markdown(f"[📞 {phone_val}](tel:{clean_phone})")
                    
                    # 3. Добавляем тонкую черту между разными людьми внутри списка
                    st.markdown("<hr style='margin: 8px 0; border: 0; border-top: 1px solid #EEEEEE;'/>", unsafe_allow_html=True)

def make_phone_callable(phone_str):
    """Вспомогательная функция для создания кликабельной ссылки на номер телефона"""
    clean_phone = str(phone_str).replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
    return f'<a href="tel:{clean_phone}" style="color: #111111; text-decoration: underline;">{phone_str}</a>'

def calculate_age(birth_date_val):
    """Техническая функция-заглушка для предотвращения конфликтов в системе"""
    return 999
