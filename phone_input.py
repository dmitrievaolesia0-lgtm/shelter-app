import streamlit as st


def format_phone(digits: str) -> str:
    """Форматирует строку из цифр в российскую маску +7 (XXX) XXX-XX-XX."""
    # Если цифр нет, показываем пустую маску
    if not digits:
        return "+7 (___) ___-__-__"

    # Ограничиваем длину до 10 цифр (не считая +7)
    digits = digits[:10]

    # Постепенно заполняем маску по мере ввода
    result = "+7 ("
    for i, d in enumerate(digits):
        if i == 3:
            result += ") "
        elif i == 6:
            result += "-"
        elif i == 8:
            result += "-"
        result += d

    # Дописываем подчеркивания для наглядности
    remaining = 10 - len(digits)
    if len(digits) < 3:
        result += "_" * len(digits)  # Внутри скобок
    return result


def render_phone_keyboard():
    """Отрисовывает экранную клавиатуру для ввода телефона."""
    st.subheader("📱 Ввод номера телефона")

    # Инициализируем хранилище для цифр, если его еще нет
    if "phone_digits" not in st.session_state:
        st.session_state.phone_digits = ""

    # Выводим текущий отформатированный номер крупным шрифтом
    formatted = format_phone(st.session_state.phone_digits)
    st.markdown(f"### `{formatted}`")

    # Сетка кнопок клавиатуры (3 колонки)
    buttons = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["Сброс", "0", "⌫"],
    ]

    for row in buttons:
        cols = st.columns(3)
        for i, button_text in enumerate(row):
            with cols[i]:
                # Делаем кнопки на всю ширину колонки
                if st.button(button_text, key=f"btn_{button_text}", use_container_width=True):
                    if button_text == "Сброс":
                        st.session_state.phone_digits = ""
                        st.rerun()
                    elif button_text == "⌫":
                        st.session_state.phone_digits = st.session_state.phone_digits[:-1]
                        st.rerun()
                    else:
                        # Добавляем цифру, только если их меньше 10
                        if len(st.session_state.phone_digits) < 10:
                            st.session_state.phone_digits += button_text
                            st.rerun()

    # Возвращаем финальный номер для сохранения в базу данных
    # Если введено все 10 цифр, возвращаем полный номер, иначе None
    if len(st.session_state.phone_digits) == 10:
        return f"+7{st.session_state.phone_digits}"
    return None


# Тестовый запуск модуля
if __name__ == "__main__":
    st.title("Тест телефонного модуля")
    phone_number = render_phone_keyboard()
    if phone_number:
        st.success(f"Номер успешно введен: {phone_number}")
    else:
        st.warning("Введите полные 10 цифр номера (после +7)")
