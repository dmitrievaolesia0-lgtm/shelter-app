import streamlit as st
import pandas as pd

def show_analytics_panel(df):
    """Модуль аналитики: Группировка и вывод жителей по административным районам со скроллом"""
    if df.empty:
        st.info("Нет данных для построения отчетов.")
        return

    st.write("---")
    st.caption("СПИСКИ ЖИТЕЛЕЙ ПО АДМИНИСТРАТИВНЫМ РАЙОНАМ")
    
    # Полный список районов для строгого соответствия структуре системы
    all_districts = ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]
    
    # Карта дней недели в двухбуквенный формат
    week_map = {
        "Понедельник": "ПН", "Вторник": "ВТ", "Среда": "СР", 
        "Четверг": "ЧТ", "Пятница": "ПТ", "Суббота": "СБ", "Воскресенье": "ВС"
    }

    # Перебираем каждый район города по очереди
    for district in all_districts:
        district_df = df[df['district'] == district]
        count_in_district = len(district_df)
        
        # Строгий текстовый заголовок без эмодзи
        district_header = f"Район: {district} (Записей: {count_in_district})"
        
        with st.expander(district_header, expanded=False):
            if district_df.empty:
                st.caption("В данном районе зарегистрированных записей не найдено.")
            else:
                # Начинаем формировать один общий HTML-блок для экономии места и плавной прокрутки
                # max-height: 240px — это высота примерно под 6-7 строк записей жителей
                html_scroll_block = """
                <div style="max-height: 240px; overflow-y: auto; padding-right: 5px; font-family: sans-serif; font-size: 14px; color: #111111; line-height: 1.6;">
                """
                
                # Собираем строки с жителями внутрь этого контейнера
                for idx, row in district_df.iterrows():
                    fio_text = row.get('fio', 'Без имени')
                    phone_val = row.get('phone', '-')
                    visit_date = row.get('visit_date', '-')
                    
                    # Генерируем ссылку для прямого звонка
                    clean_phone = str(phone_val).replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
                    callable_phone_html = f'<a href="tel:{clean_phone}" style="color: #111111; text-decoration: underline;">{phone_val}</a>'
                    
                    # Форматируем день недели
                    day_name = row.get('День недели визита', '-')
                    short_day = week_map.get(str(day_name).strip(), "-")
                    
                    # Добавляем строгий текстовый элемент (одна запись — одна строка)
                    html_scroll_block += f'<div style="margin-bottom: 8px; border-bottom: 1px solid #F3F4F6; padding-bottom: 4px;">{fio_text} | Номер телефона: {callable_phone_html} | Дата визита: {visit_date} ({short_day})</div>'
                
                html_scroll_block += "</div>"
                
                # Безопасно выводим готовый скролл-контейнер на экран планшета
                st.markdown(html_scroll_block, unsafe_allow_html=True)

def make_phone_callable(phone_str):
    """Вспомогательная функция для создания кликабельной ссылки на номер телефона"""
    clean_phone = str(phone_str).replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
    return f'<a href="tel:{clean_phone}" style="color: #111111; text-decoration: underline;">{phone_str}</a>'

def calculate_age(birth_date_val):
    """Техническая функция-заглушка для предотвращения конфликтов в системе"""
    return 999
