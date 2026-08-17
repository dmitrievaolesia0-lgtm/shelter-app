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
                # Контейнер с автопрокруткой (скроллом) для экономии места
                html_scroll_block = """
                <div style="max-height: 250px; overflow-y: auto; padding-right: 5px; font-family: sans-serif; font-size: 14px; color: #111111; line-height: 1.4;">
                """
                
                # Построчный вывод жителей без лишнего визуального шума дат
                for idx, row in district_df.iterrows():
                    fio_text = row.get('fio', 'Без имени')
                    phone_val = row.get('phone', '-')
                    
                    # Формируем прямую ссылку для совершения звонка
                    clean_phone = str(phone_val).replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
                    
                    # Аккуратная верстка: ФИО сверху, кликабельный телефон с трубкой снизу, даты полностью удалены
                    html_scroll_block += f"""
                    <div style="margin-bottom: 10px; border-bottom: 1px solid #EEEEEE; padding-bottom: 6px;">
                        <div style="font-weight: 500; color: #111111;">{fio_text}</div>
                        <div style="font-size: 13px; color: #555555; margin-top: 2px;">
                            <a href="tel:{clean_phone}" style="color: #0066CC; text-decoration: underline;">📞 {phone_val}</a>
                        </div>
                    </div>
                    """
                
                html_scroll_block += "</div>"
                
                # Безопасно рендерим структурированный список на экран
                st.markdown(html_scroll_block, unsafe_allow_html=True)

def make_phone_callable(phone_str):
    """Вспомогательная функция для создания кликабельной ссылки на номер телефона"""
    clean_phone = str(phone_str).replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
    return f'<a href="tel:{clean_phone}" style="color: #111111; text-decoration: underline;">{phone_str}</a>'

def calculate_age(birth_date_val):
    """Техническая функция-заглушка для предотвращения конфликтов в системе"""
    return 999
