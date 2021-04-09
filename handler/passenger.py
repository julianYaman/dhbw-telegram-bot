import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from main import loading_driver_search

temp_message = None
temp_driver_search_counter = 2
temp_bool = True


def create_passenger_preparation_menu(update: Update, context: CallbackContext):
    button_labels = ["Ja", "Nein", "Zurück"]
    button_list = []

    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    reply_markup = InlineKeyboardMarkup(
        build_passenger_preparation_menu(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Möchtest du deinen aktuellen Standort als Abholpunkt definieren?",
        reply_markup=reply_markup
    )


def build_passenger_preparation_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def passenger_use_current_location(update: Update, context: CallbackContext):
    global temp_message, temp_driver_search_counter
    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}
    if update.message is not None:
        temp_message = update.message.reply_text("Warte auf Standort...")
    else:
        if temp_driver_search_counter == 2:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_message.message_id,
                                          text=loading_driver_search[temp_driver_search_counter])
            temp_driver_search_counter = 0
        else:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_message.message_id,
                                          text=loading_driver_search[temp_driver_search_counter])
            temp_driver_search_counter += 1


def passenger_use_other_location(update: Update, context: CallbackContext):
    global temp_message, temp_driver_search_counter
    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}

    temp_message = update.message.reply_text("Warte auf Standort...")

    # TODO: Mit "Job" ersetzen
    while temp_bool:
        time.sleep(1)
        if temp_driver_search_counter == 2:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_message.message_id,
                                          text=loading_driver_search[temp_driver_search_counter])
            temp_driver_search_counter = 0
        else:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_message.message_id,
                                          text=loading_driver_search[temp_driver_search_counter])
            temp_driver_search_counter += 1
