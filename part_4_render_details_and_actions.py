import streamlit as st
import db_core as core
import db_dialogs as dialogs

def part_4_render_details_and_actions(links_html, row, current_district, idx, df):
    """Часть 4: Вывод строго ограниченных данных, кнопок управления и комментариев"""
    
    # Отображение статуса фотоотчета
    if links_html:
        st.markdown(f"**Фотоотчет:** {' | '.join(links_html)}", unsafe_allow_html=True)
    else:
        st.markdown("**Фотоотчет:** Не прикреплен")
    
    # Вкладка дополнительных данных: строго Номенклатура и Район
    with st.expander("📝 Дополнительные данные анкеты", expanded=False):
        st.markdown(f"**Номенклатура выданного корма:** {row.get('feed_type', '-')}")
        st.markdown(f"**Район проживания:** {current_district}")

    # БЛОК РУЧНОГО ВВОДА КОММЕНТАРИЕВ (Текст выводится обычным шрифтом)
    st.write("---")
    
    # Ключ для хранения комментария в памяти сессии, чтобы текст не пропадал
    comment_key = f"comment_field_{idx}"
    
    # Достаем ранее сохраненный комментарий из базы данных (если он там есть), иначе пустая строка
    existing_comment = row.get('comment_text', '') if 'comment_text' in row else ''
    
    # Поле ввода для оператора
    user_comment = st.text_area(
        "Комментарий к записи (введите текст):", 
        value=existing_comment,
        key=comment_key,
        placeholder="Введите служебные отметки или примечания..."
    )
    
    # Кнопка для фиксации комментария в базе данных
    if st.button("Сохранить комментарий", key=f"save_comm_btn_{idx}"):
        # Записываем комментарий напрямую в структуру данных
        row['comment_text'] = user_comment
        
        # Передаем обновленную строку в ядро базы для сохранения на сервере
        success = core.update_recipient_comment(idx, user_comment)
        if success:
            st.success("Уведомление: Комментарий успешно сохранен в базе данных.")
            core.clear_db_cache()
        else:
            st.error("Ошибка: Не удалось обновить текстовый комментарий.")

    # Системные кнопки управления
    st.write("---")
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("✏️ Редактировать", key=f"edit_{idx}", use_container_width=True):
            dialogs.edit_dialog(idx, row, df)
            core.clear_db_cache()
    with btn_col2:
        if st.button("🚨 Удалить", key=f"del_{idx}", use_container_width=True):
            dialogs.delete_dialog(idx, row.get('fio', 'Без имени'), df)
            core.clear_db_cache()
