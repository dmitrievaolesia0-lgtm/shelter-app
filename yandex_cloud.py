import streamlit as st
import pandas as pd
import io
import yadisk

YANDEX_TOKEN = st.secrets.get("YANDEX_TOKEN", "")
FILE_PATH_ON_DISK = "/shelter_base.xlsx"  # Обязательно с ведущим слэшем

def get_empty_type_client():
    return yadisk.YaDisk(token=YANDEX_TOKEN)

def get_empty_template():
    return pd.DataFrame(columns=[
        'fio', 'birth_date', 'passport_series', 'passport_number',
        'passport_date', 'passport_code', 'phone', 'district',
        'vk_link', 'address', 'feed_type', 'photo_path', 'visit_date'
    ])

def download_from_yandex():
    try:
        y = get_empty_type_client()
        if not y.check_token():
            return get_empty_template()
        
        if y.exists(FILE_PATH_ON_DISK):
            stream = io.BytesIO()
            y.download(FILE_PATH_ON_DISK, stream)
            stream.seek(0)
            return pd.read_excel(stream)
        else:
            return get_empty_template()
    except Exception:
        return get_empty_template()

def upload_to_yandex(df):
    try:
        y = get_empty_type_client()
        if not y.check_token():
            st.error("Неверный или просроченный YANDEX_TOKEN в Secrets.")
            return False
            
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        
        # Передаем байтовый поток на диск с перезаписью
        y.upload(output, FILE_PATH_ON_DISK, overwrite=True)
        return True
    except Exception as e:
        st.error(f"Ошибка при отправке файла в облако Яндекс: {str(e)}")
        return False
