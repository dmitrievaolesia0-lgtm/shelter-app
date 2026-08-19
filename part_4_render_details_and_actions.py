import streamlit as st
import pandas as pd
import db_core as core
import db_dialogs as dialogs

def part_4_render_details_and_actions(links_html, row, current_district, idx, df):
    """Часть 4: Вывод фотоотчета, сквозного комментария и кнопок управления с мгновенным обновлением."""
    
    if links_html:
        st.markdown(f"Фотоотчет: {' | '.join(links_html)}", unsafe_allow_html=True)
    else:
        st.markdown("Фотоотчет: не прикреплен")
    
    db_comment_key = f"db_comment_stored_{idx}"
    comment_input_key = f"comment_field_input_{idx}"
    
    if db_comment_key not in st.session_state:
        db_comment_key_val = row.get('comment_text', '')
        st.session_state[db_comment_key] = "" if pd.isna(db_comment_key_val) else str(db_comment_key_val).strip()
    
    current_comment_val = st.session_state[db_comment_key]
    if current_comment_val:
        st.markdown(f"Комментарий: {current_comment_val}")
    else:
        st.markdown("Комментарий: отсутствует")
        
    st.write("---")
    
    user_comment = st.text_area(
        "Добавить служебную отметку / комментарий к записи:", 
        value="", 
        key=comment_input_key,
        placeholder="Введите новый текст примечания здесь...",
        label_visibility="collapsed"
    )

    # ИСПРАВЛЕНО: Исправлен критический сдвиг отступов, вызывавший IndentationError
    if st.button("Сохранить комментарий", key=f"save_comm_btn_{idx}"):
        cleaned_comment = user_comment.strip()
        
        if cleaned_comment:
            st.session_state[db_comment_key] = cleaned_comment
            
            if core.update_recipient_comment(idx, cleaned_comment):
                st.success("Уведомление: Комментарий успешно зафиксирован.")
                st.rerun()
            else:
                st.error("Ошибка: Не удалось сохранить изменения в облако Яндекс.")
        else:
            st.error("Ошибка: Невозможно сохранить пустое текстовое поле.")

    st.write("---")
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("Редактировать", key=f"edit_{idx}", use_container_width=True):
            if hasattr(dialogs, 'edit_dialog'):
                dialogs.edit_dialog(idx, row)
            else:
                st.error("Ошибка: Компонент редактирования недоступен.")
                
    with btn_col2:
        if st.button("Удалить", key=f"del_{idx}", use_container_width=True):
            if hasattr(dialogs, 'delete_dialog'):
                fio_name = row.get('fio', 'Без имени')
                dialogs.delete_dialog(idx, fio_name)
            else:
                st.error("Ошибка: Компонент удаления недоступен.")
