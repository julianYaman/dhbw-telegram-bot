from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext
from main import loading_driver_enabling_search, DRIVER_QUERY_HANDLER, DRIVER_SET_DESTINATION, DRIVER_ENABLE_PASSENGERS_TO_SEARCH
from modules.location_handler import *

temp_driver_message = None
temp_driver_enabling_search_counter = 2


def create_driver_preparation_menu(update: Update, context: CallbackContext):
    button_labels = ["Für Mitfahrer sichtbar sein", "Zurück"]
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
        if update.effective_message.location.live_period is None:
            # Just removes the reply markup
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=context.user_data["last_message_id"],
                                          text="Bitte schicke deinen Live-Standort, damit die Suche nach Fahrern beginnen kann.")
            msg = context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Bitte schicke nun *deinen Live-Standort*, damit dich Mitfahrer finden und kontaktieren können.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                    "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]]),
                parse_mode=ParseMode.MARKDOWN
            )

            context.user_data["last_message_id"] = msg.message_id
            return DRIVER_ENABLE_PASSENGERS_TO_SEARCH

        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                      message_id=context.user_data["last_message_id"],
                                      text="Bitte schicke nun deinen Live-Standort, damit dich Mitfahrer finden und kontaktieren können.")

        temp_driver_message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=loading_driver_enabling_search[temp_driver_enabling_search_counter-1],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Sichtbarkeit beenden", callback_data="Zurück ins Startmenü")]])
        )
        set_driver_current_location(update.effective_user.id, coordinates)
    else:
        if temp_driver_enabling_search_counter == 2:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_driver_message.message_id,
                                          text=loading_driver_enabling_search[temp_driver_enabling_search_counter],
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Sichtbarkeit beenden", callback_data="Zurück ins Startmenü")]]))
            temp_driver_enabling_search_counter = 0
            set_driver_current_location(update.effective_user.id, coordinates)
        else:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_driver_message.message_id,
                                          text=loading_driver_enabling_search[temp_driver_enabling_search_counter],
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Sichtbarkeit beenden", callback_data="Zurück ins Startmenü")]]))
            temp_driver_enabling_search_counter += 1


def driver_set_destination(update: Update, context: CallbackContext):
    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}

    if update.message is not None:

        if update.effective_message.location.live_period and context.user_data["already_sent_live_location"] is False:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=context.user_data["last_message_id"],
                                          text="Wohin fährst du? Bitte teile dein Ziel als Standort mit.")
            msg = context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Wohin fährst du? Bitte teile dein Ziel *als Standort* mit.\n"
                     "Um keine Fehler bei der Benutzung zu haben, schalte *davor* bitte deinen Live-Standort aus.\n\n"
                     "Danach startet die Suche automatisch mit deinem aktuellen Standort.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                    "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]]),
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["last_message_id"] = msg.message_id
            context.user_data["already_sent_live_location"] = True
            return DRIVER_SET_DESTINATION

        button_labels = ["Ja", "Nein"]
        button_list = []

        context.user_data["already_sent_live_location"] = False

        for label in button_labels:
            button_list.append(InlineKeyboardButton(label, callback_data=label))

        reply_markup = InlineKeyboardMarkup(
            build_driver_menu(button_list, n_cols=1))

        set_driver_destination(update.effective_user.id, coordinates)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Danke! Dein Ziel wurde erfasst.\n\n"
                 f"Möchtest du nun für potentielle Mitfahrer sichtbar sein?",
            reply_markup=reply_markup
        )

        return DRIVER_QUERY_HANDLER
