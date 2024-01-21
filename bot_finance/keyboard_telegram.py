from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def _get_keyboard(
    callback_1, callback_2, name_button_prev="Выйти", name_button_next="Дальше"
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                name_button_prev,
                callback_data=callback_1,
            ),
            InlineKeyboardButton(
                name_button_next,
                callback_data=callback_2,
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
