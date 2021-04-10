from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


def create_start_menu(update: Update, context: CallbackContext):
    button_labels = ["Fahrer", "Mitfahrer", "Profil-Einstellungen", "Abmelden"]
    button_list = []

    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    reply_markup = InlineKeyboardMarkup(
        build_start_menu(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Startmenü",
        reply_markup=reply_markup
    )


def build_start_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu
