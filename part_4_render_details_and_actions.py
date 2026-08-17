import streamlit as st
import db_core as core
import db_dialogs as dialogs

def part_4_render_details_and_actions(links_html, row, current_district, idx, df):
    """Часть 4: Вывод фотоотчета, сквозного комментария и кнопок управления с мгновенным обновлением"""
    
    # 1. Вывод фотоотчета ровно один раз стандартным шрифтом
    if links_html:
        st.markdown(f"Фотоотчет: {' | '.join(links_html)}", unsafe_allow_html=True)
    else:
        st.markdown("Фотоотчет: не прикреплен")
    
    # Ключ для хранения текущего комментария в памяти сессии
    db_comment_key = f"db_comment_stored_{idx}"
    
    # Если в памяти сессии еще нет этого комментария, берем его из базы данных
    if db_comment_key not in st.session_state:
        st.session_state[db_comment_key] = row.get('comment_text', '') if 'comment_text' in row else ''
    
    # 2. Мгновенный вывод сохраненного комментария без задержек сервера
    current_comment_val = st.session_state[db_comment_key]
    if current_comment_val and str(current_comment_val).strip():
        st.markdown(f"Комментарий: {current_comment_val}")
    else:
        st.markdown("Комментарий: отсутствует")
        
    st.write("---")
    
    # Уникальный ключ для самого поля ввода текста
    comment_input_key = f"comment_field_input_{idx}"
    
    # Поле ввода текста — всегда загружается пустым, готовым к новой записи
    user_comment = st.text_area(
        "Добавить служебную отметку / комментарий к записи:", 
        value="", 
        key=comment_input_key,
        placeholder="Введите новый текст примечания здесь...",
        label_visibility="collapsed"
    )
    
    # Мгновенная фиксация данных по нажатию кнопки
    if st.button("Сохранить комментарий", key=f"save_comm_btn_{idx}"):
        if user_comment.strip():
            try:
                # 1. Мгновенно перезаписываем значение в памяти оперативной сессии
                st.session_state[db_comment_key] = str(user_comment.strip())
                
                # 2. Записываем в физическую таблицу, которая уйдет в облако
                if idx in df.index:
                    df.at[idx, 'comment_text'] = str(user_comment.strip())
                
                # 3. Полностью сбрасываем кэш загрузки, чтобы принудительно обновить базу данных
                st.cache_data.clear()
                core.clear_db_cache()
                
                st.success("Уведомление: Комментарий успешно зафиксирован.")
                st.rerun()
            except Exception as e:
                st.error("Ошибка: Не удалось обновить текстовое поле.")
        else:
            st.error("Ошибка: Невозможно сохранить пустое текстовое поле.")

    # 4. Системные кнопки действий
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
