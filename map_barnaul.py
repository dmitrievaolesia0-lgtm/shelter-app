import streamlit as st
import pandas as pd
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
    
st.markdown("<style>.leaflet-attribution-flag { display: none !important; }</style>", unsafe_allow_html=True)
def render_barnaul_map(df_recipients=None):
    """
    Отрисовывает строгую интерактивную карту Барнаула со списками людей.
    """
    st.markdown("<small style='color: #7F8C8D; font-weight: bold;'>ИНТЕРАКТИВНАЯ КАРТА РАЙОНОВ ГОРОДА</small>", unsafe_allow_html=True)
    
    # Группируем людей по районам
    people_by_district = {district: [] for district in BARNAUL_DISTRICTS.keys()}
    
    if df_recipients is not None and not df_recipients.empty and 'district' in df_recipients.columns:
        for _, row in df_recipients.iterrows():
            dist = row.get('district', '')
            if dist in people_by_district:
                people_by_district[dist].append({
                    "fio": row.get('fio', 'Без имени'),
                    "phone": row.get('phone', '-')
                })


    m = folium.Map(
        location=[53.3450, 83.7500], 
        zoom_start=11, 
        tiles="OpenStreetMap", attribution_control=False)

    # Отрисовываем маркеры на карте
    for district, coords in BARNAUL_DISTRICTS.items():
        list_of_people = people_by_district[district]
        count = len(list_of_people)
        
        # Строгие корпоративные цвета вместо яркого зеленого
        marker_color = "cadetblue" if count > 0 else "blue"
        
        # Формируем HTML-список для вывода во всплывающем окне маркера
        popup_html = f"<div style='font-family: sans-serif; font-size: 12px; min-width: 180px;'>"
        popup_html += f"<b>{district} район</b> (Всего: {count} чел.)<hr style='margin: 4px 0; border: 0; border-top: 1px solid #ccc;'>"
        
        if count > 0:
            for person in list_of_people[:10]:  # Выводим первые 10 человек в попап для компактности
                popup_html += f"• {person['fio']} ({person['phone']})<br>"
            if count > 10:
                popup_html += f"<i>и еще {count - 10} чел...</i>"
        else:
            popup_html += "<span style='color: #95A5A6;'>Нет зарегистрированных</span>"
        popup_html += "</div>"
        
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{district}: {count} чел.",
            icon=folium.Icon(color=marker_color, icon="home", prefix="fa")
        ).add_to(m)

    # Выводим карту на экран
    st_folium(m, width="100%", height=400, returned_objects=[])

    # СТРОГАЯ ТЕКСТОВАЯ НАВИГАЦИЯ ПОД КАРТОЙ
    st.write("---")
    st.markdown("<small style='color: #2C3E50; font-weight: bold;'>Списки жителей по административным районам:</small>", unsafe_allow_html=True)
    
    # Выводим районы в виде раскрывающихся списков (аккордеонов) под картой
    for district, list_of_people in people_by_district.items():
        count = len(list_of_people)
        if count > 0:
            with st.expander(f"📍 {district} район — зарегистрировано {count} чел."):
                for person in list_of_people:
                    st.markdown(f"<small style='color: #34495E;'>• <b>{person['fio']}</b> | Тел: {person['phone']}</small>", unsafe_allow_html=True)

if __name__ == "__main__":
    st.title("Тест карты")
