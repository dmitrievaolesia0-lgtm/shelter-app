import streamlit as st
import db_core as core
import db_dialogs as dialogs

def part_4_render_details_and_actions(links_html, row, current_district, idx, df):
    """Часть 4: Вывод строго ограниченных данных, кнопок управления и автономных комментариев"""
    
    # Отображение статуса фотоотчета без эмодзи и жирного шрифта
    if links_html:
        st.markdown(f"Фотоотчет: {' | '.join(links_html)}", unsafe_allow_html=True)
    else:
        st.markdown("Фотоотчет: не прикреплен")
    
    # Вкладка дополнительных данных: строго Номенклатура и Район без выделений текста
    with st.expander("Дополнительные данные анкеты", expanded=False):
        st.markdown(f"Номенклатура выданного корма: {row.get('feed_type', '-')}")
        st.markdown(f"Район проживания: {current_district}")

    st.write("---")
    
    # Блок ввода комментариев обычным системным шрифтом
    comment_key = f"comment_field_{idx}"
    existing_comment = row.get('comment_text', '') if 'comment_text' in row else ''
    
    user_comment = st.text_area(
        "Комментарий к записи (введите текст):", 
        value=existing_comment,
        key=comment_key,
        placeholder="Введите служебные отметки или примечания..."
    )
    
    # Автономное сохранение комментария в сессии данных
    if st.button("Сохранить комментарий", key=f"save_comm_btn_{idx}"):
        try:
            df.at[idx, 'comment_text'] = str(user_comment)
            st.success("Уведомление: Комментарий успешно зафиксирован в сессии базы данных.")
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error("Ошибка: Не удалось обновить текстовое поле в текущей сессии таблицы.")

    # Строгие системные кнопки управления без значков
    st.write("---")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Редактировать", key=f"edit_{idx}", use_container_width=True):
            dialogs.edit_dialog(idx, row, df)
            core.clear_db_cache()
    with btn_col2:
        if st.button("Удалить", key=f"del_{idx}", use_container_width=True):
            dialogs.delete_dialog(idx, row.get('fio', 'Без имени'), df)
            core.clear_db_cache()
