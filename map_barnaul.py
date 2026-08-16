import streamlit as st
import folium
from streamlit_folium import st_folium

# Координаты центров административных районов Барнаула
BARNAUL_DISTRICTS = {
    "Индустриальный": [53.3444, 83.6667],
    "Ленинский": [53.3750, 83.6917],
    "Железнодорожный": [53.3533, 83.7431],
    "Октябрьский": [53.3694, 83.7667],
    "Центральный": [53.3222, 83.7783]
}

def render_barnaul_map(df_recipients=None):
    """
    Отрисовывает интерактивную карту Барнаула.
    Если передан DataFrame с волонтерами/получателями, 
    подсчитывает их количество по районам и выводит маркеры.
    """
    st.subheader("🗺️ Интерактивная карта районов Барнаула")
    
    # Считаем количество людей в каждом районе
    counts = {district: 0 for district in BARNAUL_DISTRICTS.keys()}
    if df_recipients is not None and not df_recipients.empty and 'district' in df_recipients.columns:
        for dist in df_recipients['district']:
            if dist in counts:
                counts[dist] += 1

    # Создаем карту с центром в Барнауле
    m = folium.Map(location=[53.3547, 83.7698], zoom_start=11)

    # Добавляем маркеры для каждого района
    for district, coords in BARNAUL_DISTRICTS.items():
        count = counts[district]
        
        # Цвет маркера зависит от того, есть ли там люди
        marker_color = "green" if count > 0 else "blue"
        
        popup_text = f"<b>{district} район</b><br>Зарегистрировано: {count} чел."
        tooltip_text = f"{district}: {count}"
        
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=tooltip_text,
            icon=folium.Icon(color=marker_color, icon="info-sign")
        ).add_to(m)

    # Отображаем карту в Streamlit
    st_folium(m, width=700, height=450)

# Тестовый запуск модуля с искусственными данными
if __name__ == "__main__":
    import pandas as pd
    st.title("Тест карты Барнаула")
    
    # Создаем фейковые данные для проверки счетчиков
    fake_data = pd.DataFrame({
        'district': ["Индустриальный", "Индустриальный", "Центральный", "Ленинский"]
    })
    
    render_barnaul_map(fake_data)
