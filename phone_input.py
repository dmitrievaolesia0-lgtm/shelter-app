import streamlit as st

def format_phone(digits: str) -> str:
    """Форматирует строку из цифр в российскую маску. Если цифр нет — возвращает пустоту."""
    # Если пользователь еще ничего не нажал, скрываем маску полностью
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
    """Отрисовывает экранную клавиатуру для ввода телефона."""
    # Инициализируем хранилище для цифр
    if "phone_digits" not in st.session_state:
        st.session_state.phone_digits = ""

    # Выводим номер крупным шрифтом ТОЛЬКО если начали вводить цифры
    formatted = format_phone(st.session_state.phone_digits)
    if formatted:
        st.markdown(f"### Введённый номер: `{formatted}`")
    else:
        st.caption("Начните нажимать кнопки ниже, чтобы ввести номер телефона")

    # Сетка кнопок клавиатуры (3 колонки)
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

    # Возвращаем номер, если введены все 10 цифр после +7
    if len(st.session_state.phone_digits) == 10:
        return f"+7{st.session_state.phone_digits}"
    return None
