import streamlit as st
import pandas as pd
import db_analytics as analytics
import part_4_render_details_and_actions as p4

def part_3_render_view(view_mode, filtered_df, display_df, df):
    """Часть 3: Высокоскоростной и строго регламентированный вывод данных"""
    
    if filtered_df.empty:
        st.info("По заданным критериям поиска записей не найдено.")
        return

    # Внедряем строгий монохромный CSS для одноколоночной таблицы
    st.markdown("""
        <style>
            .strict-table-row {
                padding: 12px 16px;
                border-top: 1px solid #E6E8F0;
                border-bottom: 1px solid #E6E8F0;
                margin-top: -1px;
                background-color: #FAFAFA;
            }
            .strict-row-text {
                font-size: 15px;
                color: #111111;
                font-family: monospace;
            }
        </style>
    """, unsafe_allow_html=True)

    def get_short_district(dist_name):
        dist_map = {
            "Железнодорожный": "ЖД",
            "Индустриальный": "ИНД",
            "Ленинский": "ЛЕН",
            "Октябрьский": "ОКТ",
            "Центральный": "ЦЕНТР",
            "Не определен": "Н/А"
        }
        return dist_map.get(str(dist_name).strip(), "Н/А")

    # =========================================================================
    # ВАРИАНТ А: КОМПАКТНЫЙ ВИД (Зафиксирован без изменений, как вам понравилось)
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
                st.markdown(f"**Анкета: {target_fio}**")
                current_district = row.get('district', 'Не определен')
                current_phone = row.get('phone', '-')
                render_single_card_contents(row, current_phone, current_district, idx, df)

    # =========================================================================
    # ВАРИАНТ Б: ПОЛНАЯ АНКЕТА (Строгая одноколоночная таблица-реестр)
    # =========================================================================
    else:
        st.caption("ℹ️ Нажмите на строку реестра для раскрытия параметров и добавления комментариев")
        
        for idx, row in filtered_df.iterrows():
            current_district = row.get('district', 'Не определен')
            short_dist = get_short_district(current_district)
            current_phone = row.get('phone', '-')
            fio_text = row.get('fio', 'Без имени')
            
            # Строгий заголовок строки: ФИО, Телефон и Район в виде одной строки без рамок
            row_header = f"📋 {fio_text}  |  Контакты: {current_phone}  |  Район: {short_dist}"
            
            with st.expander(row_header, expanded=False):
                render_single_card_contents(row, current_phone, current_district, idx, df)


def render_single_card_contents(row, current_phone, current_district, idx, df):
    """Системный блок вывода внутренних параметров субъекта"""
    st.markdown(f"**День визита:** {row.get('День недели визита', '-')}")
    
    photo_str = row.get('photo_path', '')
    photo_person, photo_receipt = "Не указана", "Не указана"
    
    if photo_str and "|" in str(photo_path_raw := photo_str):
        try:
            parts = str(photo_path_raw).split("|")
            for part in parts:
                if "Человек:" in part: photo_person = part.replace("Человек:", "").strip()
                if "Расписка:" in part: photo_receipt = part.replace("Расписка:", "").strip()
        except: 
            pass
    
    links_html = []
    if photo_person and photo_person != "Не указана" and str(photo_person).startswith("http"):
        links_html.append(f'<a href="{photo_person}" target="_blank" style="color: #2C3E50; font-weight: bold; text-decoration: underline;">Фото получателя</a>')
    if photo_receipt and photo_receipt != "Не указана" and str(photo_receipt).startswith("http"):
        links_html.append(f'<a href="{photo_receipt}" target="_blank" style="color: #2C3E50; font-weight: bold; text-decoration: underline;">Фото расписки</a>')
    
    p4.part_4_render_details_and_actions(links_html, row, current_district, idx, df)
