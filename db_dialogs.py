import streamlit as st
import yandex_cloud as cloud

ALL_DISTRICTS = ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]

@st.dialog("Редактирование анкеты")
def edit_dialog(row_index, current_row, full_df):
    st.write(f"Изменение данных для: **{current_row['fio']}**")
    
    new_fio = st.text_input("ФИО", value=current_row.get('fio', ''))
    new_phone = st.text_input("Телефон", value=current_row.get('phone', ''))
    
    current_district = current_row.get('district', 'Не определен')
    default_idx = ALL_DISTRICTS.index(current_district) if current_district in ALL_DISTRICTS else 5
    new_district = st.selectbox("Район", ALL_DISTRICTS, index=default_idx)
    
    new_address = st.text_input("Адрес", value=current_row.get('address', ''))
    new_feed = st.text_input("Корм", value=current_row.get('feed_type', ''))
    
    if st.button("Сохранить изменения", type="primary", use_container_width=True):
        full_df.loc[row_index, 'fio'] = new_fio.strip()
        full_df.loc[row_index, 'phone'] = new_phone.strip()
        full_df.loc[row_index, 'district'] = new_district
        full_df.loc[row_index, 'address'] = new_address.strip()
        full_df.loc[row_index, 'feed_type'] = new_feed.strip()
        
        if cloud.upload_to_yandex(full_df):
            st.success("Данные успешно обновлены в облаке!")
            st.rerun()
        else:
            st.error("Не удалось сохранить изменения.")

@st.dialog("Удаление записи")
def delete_dialog(row_index, fio, full_df):
    st.warning(f"Вы уверены, что хотите НАВСЕГДА удалить из базы: **{fio}**?")
    st.write("Это действие нельзя будет отменить.")
    if st.button("🚨 ДА, УДАЛИТЬ", type="primary", use_container_width=True):
        updated_df = full_df.drop(index=row_index)
        if cloud.upload_to_yandex(updated_df):
            st.success("Запись успешно удалена!")
            st.rerun()
        else:
            st.error("Не удалось удалить запись.")
