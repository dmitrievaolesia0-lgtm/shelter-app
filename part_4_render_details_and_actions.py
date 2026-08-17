import streamlit as st
import db_core as core
import db_dialogs as dialogs

def part_4_render_details_and_actions(links_html, row, current_district, idx, df):
    """Часть 4: Вывод фотоотчета, сквозного комментария и кнопок управления"""
    
    # 1. Вывод фотоотчета ровно один раз стандартным шрифтом
    if links_html:
        st.markdown(f"Фотоотчет: {' | '.join(links_html)}", unsafe_allow_html=True)
    else:
        st.markdown("Фотоотчет: не прикреплен")
    
    # 2. Вывод сохраненного комментария через двоеточие на уровне остальных параметров
    existing_comment = row.get('comment_text', '') if 'comment_text' in row else ''
    if existing_comment and str(existing_comment).strip():
        st.markdown(f"Комментарий: {existing_comment}")
    else:
        st.markdown("Комментарий: отсутствует")
        
    st.write("---")
    
    # 3. Инструмент отправки новой заметки с автоматической очисткой поля ввода
    comment_input_key = f"comment_field_input_{idx}"
    
    user_comment = st.text_area(
        "Добавить служебную отметку / комментарий к записи:", 
        value="", # Поле ВСЕГДА пустое при загрузке, готовое к новому вводу
        key=comment_input_key,
        placeholder="Введите новый текст примечания здесь...",
        label_visibility="collapsed"
    )
    
    if st.button("Сохранить комментарий", key=f"save_comm_btn_{idx}"):
        if user_comment.strip():
            try:
                # Фиксируем обновленное значение в таблице данных
                df.at[idx, 'comment_text'] = str(user_comment.strip())
                st.success("Уведомление: Комментарий успешно зафиксирован в сессии базы данных.")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error("Ошибка: Не удалось обновить текстовое поле в таблице.")
        else:
            st.error("Ошибка: Невозможно сохранить пустое текстовое поле.")

    # 4. Регламентированные кнопки управления
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
