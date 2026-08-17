import streamlit as st
import pandas as pd
import db_analytics as analytics
import part_4_render_details_and_actions as p4

def part_3_render_view(view_mode, filtered_df, display_df, df):
    """Часть 3: Высокоскоростной, монохромный и строго регламентированный вывод данных"""
    
    if filtered_df.empty:
        st.info("По заданным критериям поиска записей не найдено.")
        return

    def get_short_district(dist_name):
        dist_map = {
            "Железнодорожный": "ЖД", "Индустриальный": "ИНД", "Ленинский": "ЛЕН",
            "Октябрьский": "ОКТ", "Центральный": "ЦЕНТР", "Не определен": "Н/А"
        }
        return dist_map.get(str(dist_name).strip(), "Н/А")

    def get_short_weekday(day_name):
        week_map = {
            "Понедельник": "ПН", "Вторник": "ВТ", "Среда": "СР", 
            "Четверг": "ЧТ", "Пятница": "ПТ", "Суббота": "СБ", "Воскресенье": "ВС"
        }
        return week_map.get(str(day_name).strip(), "-")

    # =========================================================================
    # ВАРИАНТ А: КОМПАКТНЫЙ ВИД (Зафиксирован)
    # =========================================================================
    if view_mode == "Компактный вид (Строки)":
        short_df = display_df[['fio', 'phone', 'district']].copy()
        short_df.columns = ['ФИО Получателя', 'Номер телефона', 'Район города']
        
        st.caption("ℹ️ Нажмите на любую строку с ФИО в таблице, чтобы открыть анкету человека")
        
        event_data = st.dataframe(
            short_df, 
            use_container_width=True, 
            hide_index=True,
            on_select="rerun", 
            selection_mode="single-row"
        )
        
        if event_data and "selection" in event_data and event_data["selection"]["rows"]:
            clicked_row_index = event_data["selection"]["rows"]
            target_fio = short_df.iloc[clicked_row_index]['ФИО Получателя']
            person_rows = filtered_df[filtered_df['fio'] == target_fio]
            
            for idx, row in person_rows.iterrows():
                st.write("---")
                st.markdown(f"Анкета: {target_fio}")
                current_district = row.get('district', 'Не определен')
                current_phone = row.get('phone', '-')
                render_single_card_contents(row, current_phone, current_district, idx, df, get_short_weekday)

    # =========================================================================
    # ВАРИАНТ Б: ПОЛНАЯ АНКЕТА (Строгий монохромный список)
    # =========================================================================
    else:
        st.caption("Нажмите на строку реестра для раскрытия параметров и добавления комментариев")
        
        for idx, row in filtered_df.iterrows():
            current_district = row.get('district', 'Не определен')
            fio_text = row.get('fio', 'Без имени')
            
            with st.expander(fio_text, expanded=False):
                render_single_card_contents(row, None, current_district, idx, df, get_short_weekday)


def render_single_card_contents(row, current_phone, current_district, idx, df, get_short_weekday_func):
    """Системный блок вывода внутренних параметров субъекта без жирного шрифта"""
    phone_to_call = current_phone if current_phone else row.get('phone', '-')
    callable_phone = analytics.make_phone_callable(phone_to_call)
    
    st.markdown(f"Номер телефона: {callable_phone}", unsafe_allow_html=True)
    
    short_day = get_short_weekday_func(row.get('День недели визита', '-'))
    st.markdown(f"Дата визита: {row.get('visit_date', '-')} ({short_day})")
    st.markdown(f"Район проживания: {current_district}")
    st.markdown(f"Номенклатура выданного корма: {row.get('feed_type', '-')}")
    
    # Парсинг фотоотчета
    photo_str = row.get('photo_path', '')
    photo_person, photo_receipt = "Не указана", "Не указана"
    if photo_str and "|" in str(photo_str):
        try:
            parts = str(photo_str).split("|")
            for part in parts:
                if "Человек:" in part: photo_person = part.replace("Человек:", "").strip()
                if "Расписка:" in part: photo_receipt = part.replace("Расписка:", "").strip()
        except: pass
    
    links_html = []
    if photo_person and photo_person != "Не указана" and str(photo_person).startswith("http"):
        links_html.append(f'<a href="{photo_person}" target="_blank" style="color: #2C3E50; text-decoration: underline;">Фото получателя</a>')
    if photo_receipt and photo_receipt != "Не указана" and str(photo_receipt).startswith("http"):
        links_html.append(f'<a href="{photo_receipt}" target="_blank" style="color: #2C3E50; text-decoration: underline;">Фото расписки</a>')
    
    # Внутренний сбор ссылок (в part_3 они больше не выводятся на экран, вывод строго делегирован в part_4)
    p4.part_4_render_details_and_actions(links_html, row, current_district, idx, df)
