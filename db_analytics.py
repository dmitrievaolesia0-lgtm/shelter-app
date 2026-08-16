import streamlit as st
import pandas as pd
import plotly.express as px

def make_phone_callable(phone_str):
    if not phone_str or phone_str == "-":
        return "-"
    clean_phone = "".join(filter(str.isdigit, phone_str))
    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone
    return f'<a href="tel:{clean_phone}" style="text-decoration: none; color: #2C3E50; font-weight: bold;">📞 {phone_str}</a>'

def render_analytics_charts(df):
    st.write("---")
    # Маленький, аккуратный заголовок вместо большого subheader
    st.markdown("<small style='color: #7F8C8D; font-weight: bold;'>СТАТИСТИКА РАСПРЕДЕЛЕНИЯ ДАННЫХ (СХЕМА)</small>", unsafe_allow_html=True)
    
    if df.empty:
        st.info("Нет данных для отображения статистики.")
        return

    col1, col2 = st.columns(2)
    # Строгий тонкий цвет линии (графитовый)
    line_color = "#34495E"
    
    with col1:
        st.markdown("<small style='color: #2C3E50;'>Визиты по дням недели</small>", unsafe_allow_html=True)
        if 'День недели визита' in df.columns:
            correct_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
            
            # Гарантируем наличие всех дней недели в схеме, даже если там 0 визитов
            base_df = pd.DataFrame({'День недели': correct_order})
            counts = df['День недели визита'].value_counts().reset_index()
            counts.columns = ['День недели', 'Количество']
            
            weekday_counts = pd.merge(base_df, counts, on='День недели', how='left').fillna(0)
            weekday_counts['Количество'] = weekday_counts['Количество'].astype(int)
            
            # Строим тонкую линию с точками вместо тяжелых серых столбов
            fig_week = px.line(
                weekday_counts, 
                x='День недели', 
                y='Количество',
                markers=True
            )
            fig_week.update_traces(line=dict(color=line_color, width=1.5), marker=dict(size=6, color=line_color))
            fig_week.update_layout(
                height=180, # Сделали график значительно ниже и компактнее
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=False, zeroline=False, title="", tickfont=dict(size=10)),
                yaxis=dict(showgrid=True, gridcolor='#ECF0F1', gridwidth=0.5, zeroline=False, title="", tickfont=dict(size=10), dtick=1)
            )
            st.plotly_chart(fig_week, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("Данные недоступны.")

    with col2:
        st.markdown("<small style='color: #2C3E50;'>Распределение по районам</small>", unsafe_allow_html=True)
        if 'district' in df.columns:
            all_districts = ["Железнодорожный", "Индустриальный", "Ленинский", "Октябрьский", "Центральный", "Не определен"]
            
            base_dist_df = pd.DataFrame({'Район': all_districts})
            d_counts = df['district'].value_counts().reset_index()
            d_counts.columns = ['Район', 'Количество']
            
            district_counts = pd.merge(base_dist_df, d_counts, on='Район', how='left').fillna(0)
            district_counts['Количество'] = district_counts['Количество'].astype(int)
            
            # Тонкая графическая линия распределения по районам
            fig_dist = px.line(
                district_counts, 
                x='Район', 
                y='Количество',
                markers=True
            )
            fig_dist.update_traces(line=dict(color=line_color, width=1.5), marker=dict(size=6, color=line_color))
            fig_dist.update_layout(
                height=180,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=False, zeroline=False, title="", tickfont=dict(size=10)),
                yaxis=dict(showgrid=True, gridcolor='#ECF0F1', gridwidth=0.5, zeroline=False, title="", tickfont=dict(size=10), dtick=1)
            )
            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("Данные недоступны.")
