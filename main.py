from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, \
    ConversationHandler
from consts import *
from modules.registration import *
from modules.start_menu import *
from modules.driver import *
from modules.passenger import *
from modules.profile_settings import *
from modules.profile_handler import *
from modules.location_handler import *
from modules.util import *
import ast

bot = None


def cancel(update: Update, context: CallbackContext):
    """Ends the conversation with the bot and sends a message to the user

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int: An integer which represents another status
    """

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Bye :-)"
    )

    return ConversationHandler.END


def login_query_handler(update: Update, context: CallbackContext):
    """Manages the user registration and login

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int: An integer which represents another status
    """

    query = update.callback_query
    query.answer()

    if query.data == "Registrieren":
        # Remove inline keyboard from message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        # If the user already exists, he/she will be redirected to the start menu instantly
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
        # Remove inline keyboard from message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        # Checks if the user already exists in the user storage file. The user will see a error message, that no
        # user was found
        if is_already_registered(update.effective_user.id)["type"] == "UserNotFound":
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Leider wurde kein User mit deinem Namen gefunden. Bitte registriere dich, um den Bot nutzen zu "
                     "können. "
            )
            # Creates the Login menu
            create_login(update, context)
            return LOGIN_QUERY_HANDLER
        else:
            # Logging in the user
            login_user_response = login_user(update.effective_user)

            # Handles the returned success dictionary
            if login_user_response["error"] is True:
                if login_user_response["type"] == "JSONFileError":
                    # Offering the user to restart the conversation with the bot
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Leider ist ein Fehler beim Aufrufen der Daten aufgetreten. (/start erneut)"
                    )
                    return ConversationHandler.END
                else:
                    # Offering the user to restart the conversation with the bot
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Ein unbekannter Fehler ist aufgetreten. (/start erneut)"
                    )
                    return ConversationHandler.END
            else:
                # If a user was found, show the start menu so the user can proceed with using the bot
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
    """Manages telegram users without t.me-Link

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int: An integer which represents another status
    """

    # Fetching the user_data and the started registration_data dictionary
    current_registration_data = context.user_data["registration_data"]
    # If the user sent his phone number, it will be saved as the user's "link"
    user_phone_number = update.message.contact.phone_number

    current_registration_data["link"] = user_phone_number
    current_registration_data["contact_type"] = "phone"

    # Register user with error handling
    register_user_response = register_user(current_registration_data)
    if register_user_response["error"] is True:
        if register_user_response["type"] == "JSONFileError":
            # Offering the user to restart the conversation with the bot
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Leider ist ein Fehler beim Aufrufen der Daten aufgetreten. (/start erneut)"
            )
            return ConversationHandler.END
        else:
            # Offering the user to restart the conversation with the bot
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Ein unbekannter Fehler ist aufgetreten. (/start erneut)"
            )
            return ConversationHandler.END
    else:
        if register_user_response["type"] == "SuccessfullyRegistered":
            # Have fun using the bot :)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Glückwunsch! Du hast einen neuen Account mit deiner Telefonnummer erstellt."
                     "\nViel Spaß mit LikeUber 👍"
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
    """Ends the conversation with the bot because no contact data is delivered by the user

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int: An integer which represents another status
    """

    if update.message.text == "Abbrechen":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Die Registrierung wurde abgebrochen. Mit /start kannst du wieder von vorne anfangen. :)",
        )
        context.user_data["registration_data"] = None
        return ConversationHandler.END


def driver_query_handler(update: Update, context: CallbackContext):
    """Manages the conversation with the bot if the user chose driver

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int: An integer which represents another status
    """

    query = update.callback_query
    query.answer()

    if query.data == "Für Mitfahrer sichtbar sein":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        # Set/Reset "already_sent_live_location" to false since the user will start the the function
        # from the beginning
        context.user_data["already_sent_live_location"] = False

        # Asking the user where the destination of his travel is
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Wohin fährst du? Bitte teile dein Ziel als Standort mit.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )

        # Saving the message id to be able to edit it later on
        context.user_data["last_message_id"] = msg.message_id
        return DRIVER_SET_DESTINATION
    elif query.data == "Ja":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        # Asking the live location from the user to make the driver visible in the search result list of potential
        # passengers
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bitte schicke nun deinen Live-Standort, damit dich Mitfahrer finden und kontaktieren können.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )

        # Saving the message id to be able to edit it later on
        context.user_data["last_message_id"] = msg.message_id
        return DRIVER_ENABLE_PASSENGERS_TO_SEARCH
    elif query.data == "Nein":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        # If canceled, all location data related to the user will be deleted to clean up the storage file
        delete_user_location_data(update.effective_user.id)

        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER
    elif query.data == "Zurück":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER
    elif query.data == "Zurück ins Startmenü":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        # If canceled, all location data related to the user will be deleted to clean up the storage file
        delete_user_location_data(update.effective_user.id)

        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER


def passenger_query_handler(update: Update, context: CallbackContext):
    """Manages the conversation with the bot if the user chose passenger

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int: An integer which represents another status
    """

    query = update.callback_query
    query.answer()

    if query.data == "Ja":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        # Asking the live location from the user to start searching for drivers
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bitte schicke deinen Live-Standort, damit die Suche nach Fahrern beginnen kann.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )

        # Saving the message id to be able to edit it later on
        context.user_data["last_message_id"] = msg.message_id
        # Saving the query id to be able to return a notification (unless the query timed out, then it won't work)
        context.user_data["query_id"] = update.callback_query.id
        return PASSENGER_USE_CURRENT_LOCATION_TO_PICKUP
    elif query.data == "Nein":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        # Resets "already_sent_live_location" to False to allow a fresh begin into the function
        context.user_data["already_sent_live_location"] = False

        # Asking the *static* location from the user to start searching for drivers
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bitte schicke einen Standort deiner Wahl, damit die Suche nach Fahrern beginnen kann.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )
        # Saving the message id to be able to edit it later on
        context.user_data["last_message_id"] = msg.message_id
        return PASSENGER_USE_OTHER_LOCATION_TO_PICKUP
    elif query.data == "Zurück":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER
    elif query.data == "Zurück zur Fahrerliste":
        # Show the driver list again. It is needed since we use the same message for showing the search results and
        # for the driver info.
        context.user_data["show_drivers_list"] = True

        # Asking for the key because the behaviour will be different between passengers using the
        # live location or the static location
        if "reply_markup" in context.user_data:
            # Removes the destination message which was shown when a driver was selected
            query.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=context.user_data['destination_msg_id'])
            # Redo the message and show the saved reply_markup again
            query.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=context.user_data["passenger_message_id"],
                                        text=context.user_data["full_text"],
                                        reply_markup=context.user_data["reply_markup"])
            context.user_data['destination_msg_id'] = None
        else:
            # Removes the destination message which was shown when a driver was selected
            query.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=context.user_data['destination_msg_id'])
            # Redo the message and just show the "Suche abbrechen" button since we cannot access the full_text
            # in user_data inside a Job. The search results will come back after the next Job was done.
            query.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=context.user_data["passenger_message_id"],
                                        text=context.user_data["full_text"],
                                        reply_markup=InlineKeyboardMarkup([[
                                            InlineKeyboardButton("Suche abbrechen",
                                                                 callback_data="Zurück ins Startmenü")]]
                                        ))
            # Saving the message id to be able to edit it later on
            context.user_data['destination_msg_id'] = None

    elif query.data == "Zurück ins Startmenü":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        query.edit_message_text("Suche weiterhin nach Fahrern...\n\nEine Liste mit Fahrern wird"
                                "unter dieser Nachricht automatisch angezeigt und aktualisiert.")

        # Resets all used user_data value so a fresh begin can be enabled when using the functionality again
        context.user_data["already_sent_live_location"] = False
        context.user_data["static_location"] = None
        context.job_queue.stop()

        # All location data related to the user will be deleted to clean up the storage file
        delete_user_location_data(update.effective_user.id)
        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER
    # We pass a stringified dictionary so it must be converted back to a normal dictionary before checking for keys
    # using the native [ast](https://docs.python.org/3/library/ast.html) package.
    elif ast.literal_eval(query.data)["drv_btn"]:
        # Since it actively searches for drivers in the background while looking the details of a driver, it can
        # happen that the driver info will just disappear. the next update and no info would stay long enough
        # to read. This happens because we use the same message. So we just use user_data to set a boolean
        # to allow showing the driver result list or not.
        context.user_data["show_drivers_list"] = False

        # Saving the converted data as a variable
        data = ast.literal_eval(query.data)

        # Get the contact method the user selected when registering to setup a proper message content.
        contact_type = get_user_contact_type(data["uid"])["contact_type"]

        if contact_type == "phone":
            # No "Kontaktieren" button necessary since we use the automatic conversion from phone-number-like-messages
            # in Telegram to clickable phone number call links.
            button_list = [InlineKeyboardButton("Zurück zur Fahrerliste", callback_data="Zurück zur Fahrerliste")]
        elif contact_type == "dm_link":
            # We use URLs since Telegram offers messaging user with their username and a https://t.me/ link.
            button_list = [InlineKeyboardButton("Kontaktieren", url=get_user_contact_value(data['uid'])['link']),
                           InlineKeyboardButton("Zurück zur Fahrerliste", callback_data="Zurück zur Fahrerliste")]
        else:
            # How?
            button_list = [InlineKeyboardButton("Wie?", callback_data="Zurück zur Fahrerliste")]

        # Set up a proper reply markup
        reply_markup = InlineKeyboardMarkup(
            build_button_menu(button_list, n_cols=1))

        # Get all data from the driver to show details to the passenger
        user_data = get_user_data(data["uid"])["data"]

        # Where is the driver heading?
        driver_destination = get_driver_destination(data["uid"])

        if driver_destination:
            message_text = ""
            if contact_type == "phone":
                # We use the automatic conversion from number-messages in Telegram to clickable phone number call links.
                # context.user_data["full_text"] is the saved content of the message before clicking on a user.
                message_text = context.user_data["full_text"] + f"\n\nDu hast _{user_data['name']}_ ausgewählt:" \
                                                                f"\n\nAlter: _{get_user_age(user_data['birthday'])}_" \
                                                                f"\nAuto: _{user_data['car']}_" \
                                                                f"\n\n*Kontaktieren:* +{get_user_contact_value(data['uid'])['link']}" \
                                                                f"\nDer Fahrer ist unterwegs nach: "
            elif contact_type == "dm_link":
                message_text = context.user_data["full_text"] + f"\n\nDu hast _{user_data['name']}_ ausgewählt:" \
                                                                f"\n\nAlter: _{get_user_age(user_data['birthday'])}_" \
                                                                f"\nAuto: _{user_data['car']}_" \
                                                                f"\nDer Fahrer ist unterwegs nach: "

            # Finally editing the message
            query.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=context.user_data["passenger_message_id"],
                                        text=message_text,
                                        reply_markup=reply_markup,
                                        parse_mode=ParseMode.MARKDOWN)

            # Showing the destination where the driver is heading so the user can see, if the destination fits
            # to his/her own destination
            destination_msg = query.bot.send_location(chat_id=update.effective_chat.id,
                                                      latitude=driver_destination['latitude'],
                                                      longitude=driver_destination['longitude'])

            # Saving the message id to be able to edit it later on
            context.user_data['destination_msg_id'] = destination_msg.message_id

        else:
            # This message will only be shown in extreme rare cases
            message_text = context.user_data["full_text"] + f"\n\nLeider wurde kein Ziel angegeben. " \
                                                            f"Vermutlich ist der Eintrag gelöscht worden und der " \
                                                            f"Fahrer nicht mehr aktiv. "

            query.bot.edit_message_text(chat_id=update.effective_chat.id,
                                        message_id=context.user_data["passenger_message_id"],
                                        text=message_text,
                                        reply_markup=reply_markup)


def profile_options_query_handler(update: Update, context: CallbackContext):
    """Manages the conversation with the bot if the user wants to change some profile options

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int: An integer which represents another status
    """

    query = update.callback_query
    query.answer()

    if query.data == "Name ändern":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Wie ist dein Name?"
        )
        return CHANGE_NAME
    elif query.data == "Geburtsdatum ändern":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Wann wurdest du geboren? (DD.MM.YYYY)"
        )
        return CHANGE_BIRTHDAY
    elif query.data == "Auto ändern":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Was für ein Auto fährst du?"
        )
        return CHANGE_CAR
    elif query.data == "Zurück":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))

        create_start_menu(update, context)
        return START_MENU_QUERY_HANDLER


def start_menu_query_handler(update: Update, context: CallbackContext):
    """Manages the conversation with the bot within the start_menu

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int: An integer which represents another status
    """

    query = update.callback_query
    query.answer()

    if query.data == "Fahrer":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        # Prepare the user to be a driver and using the Driver functionality
        create_driver_preparation_menu(update, context)
        return DRIVER_QUERY_HANDLER
    elif query.data == "Mitfahrer":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        # Prepare the user to be a passenger and searching for drivers
        create_passenger_preparation_menu(update, context)
        return PASSENGER_QUERY_HANDLER
    elif query.data == "Profil-Einstellungen":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        # Show all options where the user can change their data
        create_profile_options(update, context)
        return PROFILE_OPTIONS_QUERY_HANDLER
    elif query.data == "Abmelden":
        # Removes the InlineKeyboardButtons from the previous message
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        # Bye :)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Du hast dich erfolgreich abgemeldet. Du kannst den Bot wieder mit /start ausführen."
        )
        return ConversationHandler.END


def main():
    """Initializes important data, starts the bot and handles the conversation with the bot

    Returns:
        None
    """

    token = None

    # Fetching the token from data/bot.json
    # ATTENTION: DONT REMOVE IT FROM .gitignore !!!!!!!
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

    # Our one and almighty ConversationHandler
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
                MessageHandler(Filters.location, passenger_use_other_location, pass_job_queue=True),
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

# Let's go
if __name__ == "__main__":
    main()
