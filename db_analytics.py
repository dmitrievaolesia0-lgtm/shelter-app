import streamlit as st
import pandas as pd
import plotly.express as px

def make_phone_callable(phone_str):
    """Превращает номер телефона в кликабельную HTML-ссылку для звонка."""
    if not phone_str or phone_str == "-":
        return "-"
    # Очищаем номер от скобок, пробелов и дефисов для ссылки tel:
    clean_phone = "".join(filter(str.isdigit, phone_str))
    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone
    
    # Возвращаем красивую HTML-кнопку/ссылку
    return f'<a href="tel:{clean_phone}" style="text-decoration: none; color: #1f77b4; font-weight: bold;">📞 {phone_str}</a>'

def render_analytics_charts(df):
    """Строит минималистичные графики в строгом корпоративном стиле."""
    st.write("---")
    st.markdown("### 📊 Статистика распределения данных")
    
    if df.empty:
        st.info("Нет данных для отображения статистики.")
        return

    col1, col2 = st.columns(2)
    
    # Строгий графитовый цвет для основных столбцов
    corporate_dark = "#2C3E50" 
    
    with col1:
        st.markdown("**📅 Визиты по дням недели**")
        if 'День недели визита' in df.columns:
            correct_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
            
            weekday_counts = df['День недели визита'].value_counts().reset_index()
            weekday_counts.columns = ['День недели', 'Количество']
            
            weekday_counts['День недели'] = pd.Categorical(weekday_counts['День недели'], categories=correct_order, ordered=True)
            weekday_counts = weekday_counts.sort_values(by='День недели')
            
            fig_week = px.bar(
                weekday_counts, 
                x='Количество', 
                y='День недели', 
                orientation='h',
                template='plotly_white',
                category_orders={"День недели": correct_order}
            )
            # Применяем строгую стилизацию
            fig_week.update_traces(marker_color=corporate_dark, width=0.6)
            fig_week.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=False, title="", tickformat=",d"),
                yaxis=dict(showgrid=False, title="")
            )
            st.plotly_chart(fig_week, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("Данные недоступны.")

    with col2:
        st.markdown("**🏘️ Распределение по районам города**")
        if 'district' in df.columns:
            district_counts = df['district'].value_counts().reset_index()
            district_counts.columns = ['Район', 'Количество']
            district_counts = district_counts.sort_values(by='Количество', ascending=True)
            
            fig_dist = px.bar(
                district_counts, 
                x='Количество', 
                y='Район', 
                orientation='h',
                template='plotly_white'
            )
            # Применяем строгую стилизацию
            fig_dist.update_traces(marker_color="#34495E", width=0.6)
            fig_dist.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=False, title="", tickformat=",d"),
                yaxis=dict(showgrid=False, title="")
            )
            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("Данные недоступны.")






    
