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
    """Строит графики на основе текущего отфильтрованного датафрейма."""
    st.write("---")
    st.subheader("📊 Аналитика и статистика (по выбранным фильтрам)")
    
    if df.empty:
        st.info("Нет данных для построения графиков.")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("📅 Посещаемость по дням недели")
        if 'День недели визита' in df.columns:
            # Правильный порядок дней для жесткой сортировки графика
            correct_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
            
            weekday_counts = df['День недели визита'].value_counts().reset_index()
            weekday_counts.columns = ['День недели', 'Количество визитов']
            
            # Переводим колонку в категориальный тип для сохранения правильного порядка
            weekday_counts['День недели'] = pd.Categorical(weekday_counts['День недели'], categories=correct_order, ordered=True)
            weekday_counts = weekday_counts.sort_values(by='День недели')
            
            fig_week = px.bar(
                weekday_counts, 
                x='Количество визитов', 
                y='День недели', 
                orientation='h',
                color='День недели',
                template='plotly_white',
                category_orders={"День недели": correct_order} # Насильно задаем порядок на графике
            )
            fig_week.update_layout(showlegend=False, height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_week, use_container_width=True)
        else:
            st.warning("Колонка дней недели недоступна.")

    with col2:
        st.caption("🏘️ Распределение получателей по районам")
        if 'district' in df.columns:
            district_counts = df['district'].value_counts().reset_index()
            district_counts.columns = ['Район', 'Количество']
            
            fig_dist = px.pie(
                district_counts, 
                values='Количество', 
                names='Район',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_dist.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.warning("Колонка районов недоступна.")



    
