import streamlit as st
import pandas as pd
import db_analytics as analytics
import part_4_render_details_and_actions as p4

def part_3_render_view(view_mode, filtered_df, display_df, df):
    """Часть 3: Высокоскоростной и компактный вывод данных по стандартам заказчика"""
    
    if filtered_df.empty:
        st.info("По заданным критериям поиска записей не найдено.")
        return

    # Строгие деловые CSS-стили для визуального сближения элементов
    st.markdown("""
        <style>
            .styled-card-box {
                padding: 10px 14px;
                border: 1px solid #E6E8F0;
                border-radius: 4px;
                margin-bottom: 4px !important;
                background-color: #FFFFFF;
            }
            .card-header-flex {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                align-items: center;
                font-size: 15px;
            }
            .card-fio {
                font-weight: 600;
                color: #1F2937;
                margin-right: 10px;
            }
            .card-meta {
                color: #4B5563;
                font-size: 14px;
            }
            .district-badge {
                background-color: #F3F4F6;
                padding: 2px 6px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 12px;
                color: #374151;
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
    # ВАРИАНТ А: КОМПАКТНЫЙ ВИД (Интерактивная таблица с выбором по клику)
    # =========================================================================
    if view_mode == "Компактный вид (Строки)":
        # Формируем строгую таблицу БЕЗ даты визита
        short_df = display_df[['fio', 'phone', 'district']].copy()
        short_df.columns = ['ФИО Получателя', 'Номер телефона', 'Район города']
        
        st.caption("ℹ️ Нажмите на любую строку с ФИО в таблице, чтобы открыть анкету человека")
        
        # Выводим интерактивную таблицу. Результат клика записывается в переменную 'selected_row'
        event_data = st.dataframe(
            short_df, 
            use_container_width=True, 
            hide_index=True,
            on_select="rerun",  # Перезапускает интерфейс мгновенно при клике по строке
            selection_mode="single-row"  # Позволяет выбрать одну строку за раз
        )
        
        # Проверяем, кликнул ли оператор по какой-нибудь строке
        if event_data and "selection" in event_data and event_data["selection"]["rows"]:
            # Получаем индекс выбранной строки в текущей таблице
            clicked_row_index = event_data["selection"]["rows"][0]
            
            # Извлекаем ФИО человека из выбранной строки
            target_fio = short_df.iloc[clicked_row_index]['ФИО Получателя']
            
            # Находим полные данные этого человека в исходной базе
            person_rows = filtered_df[filtered_df['fio'] == target_fio]
            
            for idx, row in person_rows.iterrows():
                st.write("---")
                # Выводим анкету без лишних слов «Подробная карточка»
                st.markdown(f"**Анкета: {target_fio}**")
                current_district = row.get('district', 'Не определен')
                current_phone = row.get('phone', '-')
                render_single_card_contents(row, current_phone, current_district, idx, df)

    # =========================================================================
    # ВАРИАНТ Б: ПОЛНАЯ АНКЕТА (Компактные плитки-карточки)
    # =========================================================================
    else:
        for idx, row in filtered_df.iterrows():
            current_district = row.get('district', 'Не определен')
            short_dist = get_short_district(current_district)
            current_phone = row.get('phone', '-')
            
            st.markdown(f"""
                <div class="styled-card-box">
                    <div class="card-header-flex">
                        <div>
                            <span class="card-fio">👤 {row.get('fio', 'Без имени')}</span>
                            <span class="district-badge">{short_dist}</span>
                        </div>
                        <div class="card-meta">
                            📞 <b>{current_phone}</b> | 📅 {row.get('visit_date', '-')}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📝 Открыть архивные данные и действия", expanded=False):
                render_single_card_contents(row, current_phone, current_district, idx, df)


def render_single_card_contents(row, current_phone, current_district, idx, df):
    """Системный блок вывода внутренних параметров субъекта"""
    st.markdown(f"**День визита:** {row.get('День недели визита', '-')}")
    
    photo_str = row.get('photo_path', '')
    photo_person, photo_receipt = "Не указана", "Не указана"
    
    if photo_str and "|" in str(photo_str):
        try:
            parts = str(photo_str).split("|")
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
