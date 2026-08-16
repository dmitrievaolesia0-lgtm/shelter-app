import streamlit as st


def format_phone(digits: str) -> str:
    """Форматирует строку цифр. Если цифр нет — возвращает только +7."""
    if not digits:
        return "+7 "

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
    """Отрисовывает ввод телефона в едином стиле с раскрытием кнопок по нажатию."""
    if "phone_digits" not in st.session_state:
        st.session_state.phone_digits = ""

    # Кнопка-заглушка, которая выглядит один-в-один как стандартное текстовое поле ввода
    formatted = format_phone(st.session_state.phone_digits)

    # Переключатель состояния активности поля (имитируем фокус/нажатие на поле)
    if "phone_active" not in st.session_state:
        st.session_state.phone_active = False

    # Стилизованная надпись над полем
    st.markdown("Номер телефона *")

    # Кнопка, имитирующая поле ввода. При нажатии активирует клавиатуру
    field_label = (
        formatted if st.session_state.phone_digits else "+7 (нажмите для ввода)"
    )
    if st.button(
        field_label, key="phone_field_trigger", use_container_width=True
    ):
        st.session_state.phone_active = not st.session_state.phone_active
        st.rerun()

    # Если волонтер нажал на поле — показываем кнопки
    if st.session_state.phone_active:
        st.caption("📱 Используйте экранные клавиши для ввода номера:")
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
                    if st.button(
                        button_text,
                        key=f"btn_{button_text}",
                        use_container_width=True,
                    ):
                        if button_text == "Сброс":
                            st.session_state.phone_digits = ""
                            st.rerun()
                        elif button_text == "⌫":
                            st.session_state.phone_digits = (
                                st.session_state.phone_digits[:-1]
                            )
                            st.rerun()
                        else:
                            if len(st.session_state.phone_digits) < 10:
                                st.session_state.phone_digits += button_text
                                st.rerun()

        # Кнопка «Готово», чтобы скрыть клавиатуру после ввода
        if st.button("Готово", key="hide_phone_keys", type="secondary"):
            st.session_state.phone_active = False
            st.rerun()

    # Возвращаем номер, если введены все 10 цифр
    if len(st.session_state.phone_digits) == 10:
        return f"+7{st.session_state.phone_digits}"
    return None
