import streamlit as st
import db_core as core
import db_dialogs as dialogs

def part_4_render_details_and_actions(links_html, row, current_district, idx, df):
    """Часть 4: Вывод фотоотчета, сквозного комментария и кнопок управления с мгновенным обновлением."""
    
    # 1. Вывод фотоотчета (Выводить ТОЛЬКО здесь, из Части 3 вывод ссылок нужно убрать!)
    if links_html:
        st.markdown(f"Фотоотчет: {' | '.join(links_html)}", unsafe_allow_html=True)
    else:
        st.markdown("Фотоотчет: не прикреплен")
    
    # Ключи для сессии
    db_comment_key = f"db_comment_stored_{idx}"
    comment_input_key = f"comment_field_input_{idx}"
    
    # Инициализация комментария в сессии, если его там нет
    if db_comment_key not in st.session_state:
        db_comment_key_val = row.get('comment_text', '')
        # Защита от NaN значений из Pandas DataFrame
        st.session_state[db_comment_key] = "" if core.pd.isna(db_comment_key_val) else str(db_comment_key_val).strip()
    
    # 2. Отображение текущего комментария
    current_comment_val = st.session_state[db_comment_key]
    if current_comment_val:
        st.markdown(f"Комментарий: {current_comment_val}")
    else:
        st.markdown("Комментарий: отсутствует")
        
    st.write("---")
    
    # 3. Поле ввода нового комментария
    user_comment = st.text_area(
        "Добавить служебную отметку / комментарий к записи:", 
        value="", 
        key=comment_input_key,
        placeholder="Введите новый текст примечания здесь...",
        label_visibility="collapsed"
    )

        # Мгновенная фиксация данных по нажатию кнопки
    if st.button("Сохранить комментарий", key=f"save_comm_btn_{idx}"):
        cleaned_comment = user_comment.strip()
        
        if cleaned_comment:
            # 1. Мгновенно обновляем локальное состояние сессии для отрисовки на экране
            st.session_state[db_comment_key] = cleaned_comment
            
            # 2. Вызываем физическое сохранение в облако Яндекс через db_core
            if core.update_recipient_comment(idx, cleaned_comment):
                st.success("Уведомление: Комментарий успешно зафиксирован.")
                
                # Безопасный перезапуск интерфейса (совместимость версий Streamlit)
                if hasattr(st, "rerun"):
                    st.rerun()
                else:
                    st.experimental_rerun()
            else:
                st.error("Ошибка: Не удалось сохранить изменения в облако Яндекс.")
        else:
            st.error("Ошибка: Невозможно сохранить пустое текстовое поле.")


    # 4. Системные кнопки действий (Редактировать / Удалить)
    st.write("---")
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("Редактировать", key=f"edit_{idx}", use_container_width=True):
            if hasattr(dialogs, 'edit_dialog'):
                dialogs.edit_dialog(idx, row, df)
                if hasattr(core, 'clear_db_cache'): core.clear_db_cache()
                st.rerun()
            else:
                st.error("Ошибка: Компонент редактирования недоступен.")
                
    with btn_col2:
        if st.button("Удалить", key=f"del_{idx}", use_container_width=True):
            if hasattr(dialogs, 'delete_dialog'):
                fio_name = row.get('fio', 'Без имени')
                dialogs.delete_dialog(idx, fio_name, df)
                if hasattr(core, 'clear_db_cache'): core.clear_db_cache()
                st.rerun()
            else:
                st.error("Ошибка: Компонент удаления недоступен.")
