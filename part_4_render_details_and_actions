import streamlit as st
import db_core as core
import db_dialogs as dialogs

def part_4_render_details_and_actions(links_html, row, current_district, idx, df):
    """Часть 4: Личные данные анкеты, кнопки управления (изменить/удалить)"""
    if links_html:
        st.markdown(f"**Фотоотчет:** {' | '.join(links_html)}", unsafe_allow_html=True)
    else:
        st.markdown("**Фотоотчет:** Не прикреплен")
    
    with st.expander("📝 Дополнительные данные анкеты", expanded=False):
        st.markdown(f"**Номенклатура выданного корма:** {row.get('feed_type', '-')}")
        st.markdown(f"**Район проживания:** {current_district}")
        st.markdown(f"**Адрес проживания:** {row.get('address', '-')}")
        st.markdown(f"**Паспортные данные:** {row.get('passport_series', '-')} {row.get('passport_number', '-')}")
        st.markdown(f"**Подразделение:** {row.get('passport_code', '-')}")
        st.markdown(f"**Дата рождения:** {row.get('birth_date', '-')} (Возраст: {row.get('Возраст')})")

        vk_url = row.get('vk_link', '')
        vk_deeplink = core.make_vk_deeplink(vk_url)
        
        if vk_deeplink:
            st.markdown(
                f"**Личная страница ВК:** "
                f"<a href='{vk_deeplink}' target='_blank' style='color: #1f77b4; font-weight: bold; text-decoration: underline;'>"
                f"📱 Открыть в приложении ВК"
                f"</a>", 
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"**Личная страница ВК:** -")

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
