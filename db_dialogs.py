import streamlit as st
import pandas as pd
import db_core as core
import yandex_cloud as cloud

ALL_DISTRICTS = ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]

@st.dialog("Редактирование анкеты")
def edit_dialog(row_index, current_row, _ignored_df=None):
    """Модальное окно редактирования анкеты с защитой от перезаписи базы данных."""
    # Получаем исходные ФИО и телефон для точечного поиска в базе данных
    original_fio = str(current_row.get('fio', '')).strip()
    original_phone = str(current_row.get('phone', '')).strip()
    
    st.write(f"Изменение данных для: **{original_fio}**")
    
    # Форма редактирования
    new_fio = st.text_input("ФИО", value=original_fio)
    new_phone = st.text_input("Телефон", value=original_phone)
    
    current_district = current_row.get('district', 'Не определен')
    default_idx = ALL_DISTRICTS.index(current_district) if current_district in ALL_DISTRICTS else 5
    new_district = st.selectbox("Район", ALL_DISTRICTS, index=default_idx)
    
    new_address = st.text_input("Адрес", value=current_row.get('address', ''))
    new_feed = st.text_input("Корм", value=current_row.get('feed_type', ''))
    
    if st.button("Сохранить изменения", type="primary", use_container_width=True):
        # Скачиваем самую свежую версию базы данных перед сохранением
        fresh_df = core.cached_download()
        
        if fresh_df.empty:
            st.error("Ошибка: База данных пуста или недоступна.")
            return

        # Ищем строку по ФИО и Телефону (защита от смещения индексов при фильтрации)
        match_mask = (fresh_df['fio'].astype(str).str.strip() == original_fio) & \
                     (fresh_df['phone'].astype(str).str.strip() == original_phone)
        
        matched_indices = fresh_df[match_mask].index
        
        if len(matched_indices) == 0:
            st.error("Ошибка: Данный человек не найден в актуальной базе (возможно, уже удален).")
            return
            
        target_idx = matched_indices[0]
        
        # Точечно обновляем данные в свежем датафрейме
        fresh_df.at[target_idx, 'fio'] = new_fio.strip()
        fresh_df.at[target_idx, 'phone'] = new_phone.strip()
        fresh_df.at[target_idx, 'district'] = new_district
        fresh_df.at[target_idx, 'address'] = new_address.strip()
        fresh_df.at[target_idx, 'feed_type'] = new_feed.strip()
        
        # Отправляем обновленную свежую базу в облако
        if cloud.upload_to_yandex(fresh_df):
            core.clear_db_cache()  # Сбрасываем кэш загрузки
            st.success("Данные успешно обновлены в облаке!")
            st.rerun()
        else:
            st.error("Не удалось сохранить изменения в Яндекс Облако.")


@st.dialog("Удаление записи")
def delete_dialog(row_index, fio, _ignored_df=None):
    """Модальное окно удаления записи с гарантией точечного удаления."""
    # Для безопасного удаления нам нужны точные ФИО и телефон из текущей строки
    # (Передаем имя как строку, но для надежности вытаскиваем точные данные)
    st.warning(f"Вы уверены, что хотите НАВСЕГДА удалить из базы: **{fio}**?")
    st.write("Это действие нельзя будет отменить.")
    
    # Чтобы удаление было точным, нам нужен контекст строки. 
    # Так как мы не хотим передавать весь row, используем имя для подтверждения.
    if st.button("🚨 ДА, УДАЛИТЬ", type="primary", use_container_width=True):
        fresh_df = core.cached_download()
        
        if fresh_df.empty:
            st.error("Ошибка: База данных пуста.")
            return
            
        # Находим строку по ФИО
        matched_indices = fresh_df[fresh_df['fio'].astype(str).str.strip() == str(fio).strip()].index
        
        if len(matched_indices) == 0:
            st.error("Ошибка: Запись уже удалена или изменена.")
            return
            
        # Удаляем строго найденный физический индекс в актуальной базе
        target_idx = matched_indices[0]
        fresh_df = fresh_df.drop(index=target_idx).reset_index(drop=True)
        
        if cloud.upload_to_yandex(fresh_df):
            core.clear_db_cache()  # Сбрасываем кэш
            st.success("Запись успешно удалена!")
            st.rerun()
        else:
            st.error("Не удалось удалить запись из Яндекс Облака.")
