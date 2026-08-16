import streamlit as st

def format_phone(digits: str) -> str:
    """Форматирует строку из цифр в российскую маску. Если цифр нет — возвращает пустоту."""
    if not digits:
        return ""
    digits = digits[:10]
    result = "+7 ("
    for i, d in enumerate(digits):
        if i == 3:
            result += ") "
        elif i == 6:
            result += "-"
        elif i == 8:
            result += "-"
        result += d
    return result

def render_phone_keyboard():
    """Отрисовывает экранную клавиатуру, которая раскрывается по требованию."""
    if "phone_digits" not in st.session_state:
        st.session_state.phone_digits = ""

    formatted = format_phone(st.session_state.phone_digits)
    
    # Имитация интерактивного поля: показываем текущий номер телефона
    display_text = formatted if formatted else "Нажмите 'Включить ввод', чтобы набрать номер"
    st.info(f"📱 Номер телефона: {display_text}")
    
    # Чекбокс-переключатель, который заменяет клик по столбцу на телефоне
    show_keys = st.checkbox("⌨️ Включить ввод / Открыть клавиши телефона", value=False)
    
    if show_keys:
        st.write("Нажимайте на кнопки для ввода:")
        buttons = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["Сброс", "0", "⌫"]
        ]

        for row in buttons:
            cols = st.columns(3)
            for i, button_text in enumerate(row):
                with cols[i]:
                    if st.button(button_text, key=f"btn_{button_text}", use_container_width=True):
                        if button_text == "Сброс":
                            st.session_state.phone_digits = ""
                            st.rerun()
                        elif button_text == "⌫":
                            st.session_state.phone_digits = st.session_state.phone_digits[:-1]
                            st.rerun()
                        else:
                            if len(st.session_state.phone_digits) < 10:
                                st.session_state.phone_digits += button_text
                                st.rerun()

    # Возвращаем номер, если введены все 10 цифр
    if len(st.session_state.phone_digits) == 10:
        return f"+7{st.session_state.phone_digits}"
    return None
