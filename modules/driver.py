from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from main import loading_driver_enabling_search, DRIVER_QUERY_HANDLER
from modules.location_handler import *

temp_driver_message = None
temp_driver_enabling_search_counter = 2


def create_driver_preparation_menu(update: Update, context: CallbackContext):
    button_labels = ["Suche Mitfahrer", "Zurück"]
    button_list = []

    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    reply_markup = InlineKeyboardMarkup(
        build_driver_menu(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Wie möchtest du weiter vorgehen?",
        reply_markup=reply_markup
    )


def build_driver_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def driver_enable_passengers_searching(update: Update, context: CallbackContext):
    global temp_driver_message, temp_driver_enabling_search_counter
    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}
    if update.message is not None:
        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                      message_id=context.user_data["last_message_id"],
                                      text="Bitte schicke nun deinen Live-Standort, damit dich Mitfahrer finden und kontaktieren können.")

        temp_driver_message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=loading_driver_enabling_search[temp_driver_enabling_search_counter-1],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )
        set_driver_current_location(update.effective_user.id, coordinates)
    else:
        if temp_driver_enabling_search_counter == 2:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_driver_message.message_id,
                                          text=loading_driver_enabling_search[temp_driver_enabling_search_counter],
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]]))
            temp_driver_enabling_search_counter = 0
            set_driver_current_location(update.effective_user.id, coordinates)
        else:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_driver_message.message_id,
                                          text=loading_driver_enabling_search[temp_driver_enabling_search_counter],
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]]))
            temp_driver_enabling_search_counter += 1


def driver_set_destination(update: Update, context: CallbackContext):
    context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                  message_id=context.user_data["last_message_id"],
                                  text="Wohin fährst du? Bitte teile dein Ziel als Standort mit.")
    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}
    if update.message is not None:
        button_labels = ["Ja", "Nein"]
        button_list = []

        for label in button_labels:
            button_list.append(InlineKeyboardButton(label, callback_data=label))

        reply_markup = InlineKeyboardMarkup(
            build_driver_menu(button_list, n_cols=1))

        set_driver_destination(update.effective_user.id, coordinates)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Danke! Möchtest du nun für potentielle Mitfahrer sichtbar sein?",
            reply_markup=reply_markup
        )

    return DRIVER_QUERY_HANDLER
