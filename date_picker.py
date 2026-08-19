import streamlit as st
from datetime import date

def render_date_picker(label="Дата рождения1", key_prefix="birth"):
    """Минималистичный выбор даты рождения в едином стиле с текстовыми полями."""
    selected_date = st.date_input(
        label=label, 
        value=date(1990, 1, 1),        
        min_value=date(1930, 1, 1),    
        max_value=date(2026, 12, 31),  
        key=f"{key_prefix}_calendar",
        format="DD.MM.YYYY"            
    )
    return selected_date.strftime('%Y-%m-%d')

if __name__ == "__main__":
    res_date = render_date_picker()
