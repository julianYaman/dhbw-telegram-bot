from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, \
    ConversationHandler
from consts import *
from modules.registration import *
from modules.start_menu import *
from modules.driver import *
from modules.passenger import *
from modules.profile_settings import *
from modules.location_handler import *
from modules.util import *
import ast

bot = None


def cancel(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Bye :-)"
    )

    return ConversationHandler.END


def login_query_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "Registrieren":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))  # Remove inline keyboard from message

        if is_already_registered(update.effective_user.id)["type"] == "UserFound":
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Du hast dich bereits registriert, du wirst nun eingeloggt."
            )
            create_start_menu(update, context)
            return START_MENU_QUERY_HANDLER
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=questions[0]
            )

            return ASK_NAME

    elif query.data == "Einloggen":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        if is_already_registered(update.effective_user.id)["type"] == "UserNotFound":
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Leider wurde kein User mit deinem Namen gefunden. Bitte registriere dich, um den Bot nutzen zu "
                     "können. "
            )
            create_login(update, context)
            return LOGIN_QUERY_HANDLER
        else:
            login_user_response = login_user(update.effective_user)

            if login_user_response["error"] is True:
                if login_user_response["type"] == "JSONFileError":
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Leider ist ein Fehler beim Aufrufen der Daten aufgetreten."
                    )
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Ein unbekannter Fehler ist aufgetreten."
                    )
            else:
                if login_user_response["type"] == "UserFound":
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"Du hast dich erfolgreich eingeloggt! Willkommen zurück, "
                             f"{login_user_response['name']}"
                    )
                    create_start_menu(update, context)
                    return START_MENU_QUERY_HANDLER
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Keine Ahnung was passiert ist, aber es hat funktioniert."
                    )
                    create_start_menu(update, context)
                    return START_MENU_QUERY_HANDLER


def register_with_contact_callback(update: Update, context: CallbackContext):
    current_registration_data = context.user_data["registration_data"]
    user_phone_number = update.message.contact.phone_number

    current_registration_data["link"] = user_phone_number
    current_registration_data["contact_type"] = "phone"

    # Register user with error handling
    register_user_response = register_user(current_registration_data)
    if register_user_response["error"] is True:
        if register_user_response["type"] == "JSONFileError":
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Leider ist ein Fehler beim Aufrufen der Daten aufgetreten."
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Ein unbekannter Fehler ist aufgetreten."
            )
    else:
        if register_user_response["type"] == "SuccessfullyRegistered":
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Glückwunsch! Du hast einen neuen Account erstellt."
            )
            create_start_menu(update, context)
            return START_MENU_QUERY_HANDLER
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Keine Ahnung was passiert ist, aber es hat funktioniert."
            )
            create_start_menu(update, context)
            return START_MENU_QUERY_HANDLER


def register_cancel_with_text_callback(update: Update, context: CallbackContext):
    if update.message.text == "Abbrechen":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Die Registrierung wurde abgebrochen. Mit /start kannst du wieder von vorne anfangen. :)",
        )
        context.user_data["registration_data"] = None
        return ConversationHandler.END


def driver_query_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "Für Mitfahrer sichtbar sein":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        context.user_data["already_sent_live_location"] = False
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Wohin fährst du? Bitte teile dein Ziel als Standort mit.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )
        context.user_data["last_message_id"] = msg.message_id
        return DRIVER_SET_DESTINATION
    elif query.data == "Ja":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bitte schicke nun deinen Live-Standort, damit dich Mitfahrer finden und kontaktieren können.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )
        context.user_data["last_message_id"] = msg.message_id
        return DRIVER_ENABLE_PASSENGERS_TO_SEARCH
    elif query.data == "Nein":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        delete_user_location_data(update.effective_user.id)
        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER
    elif query.data == "Zurück":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER
    elif query.data == "Zurück ins Startmenü":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        delete_user_location_data(update.effective_user.id)
        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER


def passenger_query_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "Ja":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bitte schicke deinen Live-Standort, damit die Suche nach Fahrern beginnen kann.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )
        context.user_data["last_message_id"] = msg.message_id
        context.user_data["query_id"] = update.callback_query.id
        return PASSENGER_USE_CURRENT_LOCATION_TO_PICKUP
    elif query.data == "Nein":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        context.user_data["already_sent_live_location"] = False
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bitte schicke einen Standort deiner Wahl, damit die Suche nach Fahrern beginnen kann.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )
        context.user_data["last_message_id"] = msg.message_id
        return PASSENGER_USE_OTHER_LOCATION_TO_PICKUP
    elif query.data == "Zurück":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER
    elif query.data == "Zurück zur Fahrerliste":
        context.user_data["show_drivers_list"] = True
        query.bot.delete_message(chat_id=update.effective_chat.id, message_id=context.user_data['destination_msg_id'])
        query.bot.edit_message_text(chat_id=update.effective_chat.id,
                                    message_id=context.user_data["passenger_message_id"],
                                    text=context.user_data["full_text"],
                                    reply_markup=context.user_data["reply_markup"])
        context.user_data['destination_msg_id'] = None
    elif query.data == "Zurück ins Startmenü":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        context.user_data["already_sent_live_location"] = False
        delete_user_location_data(update.effective_user.id)
        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER
    elif ast.literal_eval(query.data)["drv_btn"]:
        context.user_data["show_drivers_list"] = False
        data = ast.literal_eval(query.data)

        button_list = [InlineKeyboardButton("Kontaktieren", url=get_user_dm_link(data["uid"])["link"]),
                       InlineKeyboardButton("Zurück zur Fahrerliste", callback_data="Zurück zur Fahrerliste")]

        reply_markup = InlineKeyboardMarkup(
            build_button_menu(button_list, n_cols=1))

        user_data = get_user_data(data["uid"])["data"]

        driver_destination = get_driver_destination(data["uid"])
        if driver_destination:
            message_text = context.user_data["full_text"] + f"\n\nDu hast _{user_data['name']}_ ausgewählt:" \
                                                            f"\n\nAlter: _{get_user_age(user_data['birthday'])}_" \
                                                            f"\nAuto: _{user_data['car']}_\nDer Fahrer ist unterwegs " \
                                                            f"nach: "

            query.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=context.user_data["passenger_message_id"],
                                        text=message_text,
                                        reply_markup=reply_markup,
                                        parse_mode=ParseMode.MARKDOWN)

            destination_msg = query.bot.send_location(chat_id=update.effective_chat.id,
                                                      latitude=driver_destination['latitude'],
                                                      longitude=driver_destination['longitude'])

            context.user_data['destination_msg_id'] = destination_msg.message_id

        else:
            message_text = context.user_data["full_text"] + f"\n\nLeider wurde kein Ziel angegeben. " \
                                                            f"Vermutlich ist der Eintrag gelöscht worden und der " \
                                                            f"Fahrer nicht mehr aktiv. "

            query.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=context.user_data["passenger_message_id"],
                                        text=message_text,
                                        reply_markup=reply_markup)


def profile_options_query_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "Name ändern":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Wie ist dein Name?"
        )
        return CHANGE_NAME
    elif query.data == "Geburtsdatum ändern":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Wann wurdest du geboren?"
        )
        return CHANGE_BIRTHDAY
    elif query.data == "Auto ändern":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Was für ein Auto fährst du?"
        )
        return CHANGE_CAR
    elif query.data == "Zurück":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER


def start_menu_query_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "Fahrer":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        create_driver_preparation_menu(update, context)
        return DRIVER_QUERY_HANDLER
    elif query.data == "Mitfahrer":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        create_passenger_preparation_menu(update, context)
        return PASSENGER_QUERY_HANDLER
    elif query.data == "Profil-Einstellungen":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        create_profile_options(update, context)
        return PROFILE_OPTIONS_QUERY_HANDLER
    elif query.data == "Abmelden":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Du hast dich erfolgreich abgemeldet. Du kannst den Bot wieder mit /start ausführen."
        )
        return ConversationHandler.END


def main():
    token = None

    with open('data/bot.json', 'r') as config_file:
        try:
            data = json.load(config_file)
            token = data['token']
        except:
            print("Error occurred when trying to open the file bot.json")
            quit()

    global bot
    bot = Updater(token=token, use_context=True)

    bot.start_polling()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', create_login)],
        states={
            LOGIN_QUERY_HANDLER: [CallbackQueryHandler(login_query_handler)],
            ASK_NAME: [MessageHandler(Filters.text, ask_name)],
            ASK_BIRTHDAY: [MessageHandler(Filters.text, ask_birthday)],
            ASK_CAR: [MessageHandler(Filters.text, ask_car)],
            CONTACT_OPTIONS_MESSAGE_HANDLER: [
                MessageHandler(Filters.contact, register_with_contact_callback),
                MessageHandler(Filters.text, register_cancel_with_text_callback)
            ],
            START_MENU_QUERY_HANDLER: [CallbackQueryHandler(start_menu_query_handler)],
            DRIVER_QUERY_HANDLER: [CallbackQueryHandler(driver_query_handler)],
            DRIVER_SET_DESTINATION: [
                MessageHandler(Filters.location, driver_set_destination),
                CallbackQueryHandler(driver_query_handler)
            ],
            DRIVER_ENABLE_PASSENGERS_TO_SEARCH: [
                MessageHandler(Filters.location, driver_enable_passengers_searching),
                CallbackQueryHandler(driver_query_handler)
            ],
            PASSENGER_QUERY_HANDLER: [CallbackQueryHandler(passenger_query_handler)],
            PASSENGER_USE_CURRENT_LOCATION_TO_PICKUP: [
                MessageHandler(Filters.location, passenger_use_current_location),
                CallbackQueryHandler(passenger_query_handler)
            ],
            PASSENGER_USE_OTHER_LOCATION_TO_PICKUP: [
                MessageHandler(Filters.location, passenger_use_other_location),
                CallbackQueryHandler(passenger_query_handler)
            ],
            PROFILE_OPTIONS_QUERY_HANDLER: [CallbackQueryHandler(profile_options_query_handler)],
            CHANGE_NAME: [MessageHandler(Filters.text, change_name)],
            CHANGE_BIRTHDAY: [MessageHandler(Filters.text, change_birthday)],
            CHANGE_CAR: [MessageHandler(Filters.text, change_car)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    bot.dispatcher.add_handler(conversation_handler)

    bot.idle()


if __name__ == "__main__":
    main()
