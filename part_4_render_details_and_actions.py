import streamlit as st
import db_core as core
import db_dialogs as dialogs

def part_4_render_details_and_actions(links_html, row, current_district, idx, df):
    """Часть 4: Вывод строго ограниченных данных анкеты и кнопок управления"""
    if links_html:
        st.markdown(f"**Фотоотчет:** {' | '.join(links_html)}", unsafe_allow_html=True)
    else:
        st.markdown("**Фотоотчет:** Не прикреплен")
    
    # В блоке дополнительных данных оставлены ТОЛЬКО номенклатура и район
    with st.expander("📝 Дополнительные данные анкеты", expanded=False):
        st.markdown(f"**Номенклатура выданного корма:** {row.get('feed_type', '-')}")
        st.markdown(f"**Район проживания:** {current_district}")

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
