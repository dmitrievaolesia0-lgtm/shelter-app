import streamlit as st


def format_phone(digits: str) -> str:
    """Форматирует строку цифр в российскую маску."""
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
    """Отрисовывает ввод телефона с защитой от недобора цифр и режимом 'Иной номер'."""
    # Инициализируем переменные в памяти приложения
    if "phone_digits" not in st.session_state:
        st.session_state.phone_digits = ""
    if "phone_active" not in st.session_state:
        st.session_state.phone_active = False
    if "is_other_format" not in st.session_state:
        st.session_state.is_other_format = False
    if "other_phone_text" not in st.session_state:
        st.session_state.other_phone_text = ""

    st.markdown("Номер телефона *")

    # --- РЕЖИМ 1: ИНОЙ ФОРМАТ НОМЕРА (РУЧНОЙ ВВОД) ---
    if st.session_state.is_other_format:
        # Поле ручного ввода в той же стилистике
        manual_input = st.text_input(
            "Введите номер вручную (любой формат)",
            value=st.session_state.other_phone_text,
            placeholder="Например, +73852... или +79...",
            label_visibility="collapsed",
            key="manual_phone_field",
        )
        st.session_state.other_phone_text = manual_input

        # Кнопка возврата к обычной клавиатуре
        if st.button("Вернуться к стандартному вводу", key="back_to_std"):
            st.session_state.is_other_format = False
            st.session_state.phone_digits = ""
            st.rerun()

        # Возвращаем текст, если он не пустой
        return (
            manual_input.strip() if manual_input.strip() else "НЕ_ЗАПОЛНЕН"
        )

    # --- РЕЖИМ 2: СТАНДАРТНАЯ КЛАВИАТУРА ---
    else:
        formatted = format_phone(st.session_state.phone_digits)

        # Вывод поля-кнопки
        if len(st.session_state.phone_digits) > 0 and len(
            st.session_state.phone_digits
        ) < 10:
            # Если начали вводить, но цифр мало — подсвечиваем предупреждением
            field_label = f"{formatted} ⚠️ (нужно 10 цифр)"
        else:
            field_label = (
                formatted if st.session_state.phone_digits else "+7 (нажмите)"
            )

        if st.button(
            field_label, key="phone_field_trigger", use_container_width=True
        ):
            st.session_state.phone_active = not st.session_state.phone_active
            st.rerun()

        # Кнопки телефона открываются по клику
        if st.session_state.phone_active:
            st.caption("📱 Нажимайте экранные клавиши:")
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
                                    st.session_state.phone_digits += (
                                        button_text
                                    )
                                    st.rerun()

            # Добавляем кнопку переключения на иной формат
            if st.button(
                "📝 Иной формат номера (городской / другая страна)",
                use_container_width=True,
            ):
                st.session_state.is_other_format = True
                st.session_state.phone_active = False
                st.rerun()

            if st.button("Готово", key="hide_phone_keys", type="secondary"):
                st.session_state.phone_active = False
                st.rerun()

        # Возвращаем номер ТОЛЬКО если введены все 10 цифр. Иначе возвращаем маркер ошибки.
        if len(st.session_state.phone_digits) == 10:
            return f"+7{st.session_state.phone_digits}"
        elif len(st.session_state.phone_digits) == 0:
            return "НЕ_ЗАПОЛНЕН"
        else:
            return "ОШИБКА_ДЛИНЫ"
