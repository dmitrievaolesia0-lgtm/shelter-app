import streamlit as st
import pandas as pd
import requests
import io

YANDEX_TOKEN = st.secrets.get("YANDEX_TOKEN", "")
FILE_PATH_ON_DISK = "shelter_base.xlsx"

# Шаблон таблицы со всеми нужными колонками
def get_empty_template():
    return pd.DataFrame(columns=[
        'fio', 'birth_date', 'passport_series', 'passport_number',
        'passport_date', 'passport_code', 'phone', 'district',
        'vk_link', 'address', 'feed_type', 'photo_path', 'visit_date'
    ])

def download_from_yandex():
    url = f"https://yandex.net{FILE_PATH_ON_DISK}"
    headers = {"Authorization": f"OAuth {YANDEX_TOKEN}"}
    
    try:
        res = requests.get(url, headers=headers).json()
        download_url = res.get("href")
        if not download_url:
            return get_empty_template()
            
        file_res = requests.get(download_url)
        if file_res.status_code == 200:
            return pd.read_excel(io.BytesIO(file_res.content))
        return get_empty_template()
    except:
        return get_empty_template()

def upload_to_yandex(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    
    url = f"https://yandex.net{FILE_PATH_ON_DISK}&overwrite=true"
    headers = {"Authorization": f"OAuth {YANDEX_TOKEN}"}
    try:
        res = requests.get(url, headers=headers).json()
        upload_url = res.get("href")
        if upload_url:
            put_res = requests.put(upload_url, data=output.getvalue())
            # ИСПРАВЛЕНО НАВСЕГДА: Четко проверяем успешные коды ответа 200 или 201
            if put_res.status_code == 200 or put_res.status_code == 201:
                return True
            else:
                st.error(f"Яндекс.Диск отклонил запись файла. Код ошибки сервера: {put_res.status_code}")
        else:
            st.error("Не удалось получить прямую ссылку для загрузки. Проверьте ваш YANDEX_TOKEN в Secrets.")
        return False
    except Exception as e:
        st.error(f"Сбой сети при отправке файла в облако Яндекс: {str(e)}")
        return False

