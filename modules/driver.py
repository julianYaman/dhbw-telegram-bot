from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext
from main import loading_driver_enabling_search, DRIVER_QUERY_HANDLER, DRIVER_SET_DESTINATION, \
    DRIVER_ENABLE_PASSENGERS_TO_SEARCH
from modules.location_handler import *
from modules.util import *

temp_driver_message = None
temp_driver_enabling_search_counter = 2


def create_driver_preparation_menu(update: Update, context: CallbackContext) -> None:
    """Creates the menu which the user can use to prepare using the functions as a *driver*.

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        None
    """

    button_labels = ["Für Mitfahrer sichtbar sein", "Zurück"]
    button_list = []

    # Preparing and appending all buttons for being used in a InlineKeyboardMarkup
    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    # Building the menu with the modules.util build_button_menu function
    reply_markup = InlineKeyboardMarkup(
        build_button_menu(button_list, n_cols=1))

    # Sending the driver preparation menu with InlineKeyboardButtons
    # Ask user how to proceed from here ("Für Mitfahrer sichtbar sein" / "Zurück")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Wie möchtest du weiter vorgehen?",
        reply_markup=reply_markup
    )


def driver_enable_passengers_searching(update: Update, context: CallbackContext) -> int:
    """Makes driver visible and enables passengers to search for them if they are in the given radius.

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int: An integer which represents another status
    """

    # Global accessed variables
    # temp_driver_message -> will be used to update the same message
    # temp_driver_enabling_search_counter -> will be used to create an loading animation
    global temp_driver_message, temp_driver_enabling_search_counter

    # User sends coordinations to set and update the current location of the driver in the database
    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}

    # update.message *is* None, when the next location update happens
    # after the user shared his location live in the chat.
    if update.message is not None:
        # If live_period is None, we know that the sent location has no update interval and thus not a live location
        if update.effective_message.location.live_period is None:
            # Just removes the reply markup from the previous message
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=context.user_data["last_message_id"],
                                          text="Bitte schicke deinen Live-Standort, damit die Suche nach Fahrern beginnen kann.")

            # Declaring the sent message to a variable so it can be edited later on
            msg = context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Bitte schicke nun *deinen Live-Standort*, damit dich Mitfahrer finden und kontaktieren können.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                    "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]]),
                parse_mode=ParseMode.MARKDOWN
            )

            context.user_data["last_message_id"] = msg.message_id
            # Returns DRIVER_ENABLE_PASSENGERS_TO_SEARCH since a new location message is necessary to receive.
            return DRIVER_ENABLE_PASSENGERS_TO_SEARCH

        # Removes the buttons for a cleaner chat history
        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                      message_id=context.user_data["last_message_id"],
                                      text="Bitte schicke nun deinen Live-Standort, damit dich Mitfahrer finden und kontaktieren können.")

        # Declaring the message to a global variable
        temp_driver_message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=loading_driver_enabling_search[temp_driver_enabling_search_counter - 1],
            # -1 because it would throw a "BadRequest" error because this message
            # would be the same after being edited in the else-block below
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Sichtbarkeit beenden", callback_data="Zurück ins Startmenü")]])
        )

        # Inserts the drivers' current location to the data storage file
        set_driver_current_location(update.effective_user.id, coordinates)
    else:
        # Initially, temp_driver_enabling_search_counter starts with 2 so it will show
        # three dots at the end of the "search" sentence. It updates itself with the help of the location updates sent
        # by the live location.
        if temp_driver_enabling_search_counter == 2:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_driver_message.message_id,
                                          text=loading_driver_enabling_search[temp_driver_enabling_search_counter],
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                              "Sichtbarkeit beenden", callback_data="Zurück ins Startmenü")]]))
            # Sets it to 0 so the first dot would be the next one
            temp_driver_enabling_search_counter = 0

            # Everytime when temp_driver_enabling_search_counter is 2, the location will
            # be updated to reduce local storage traffic
            set_driver_current_location(update.effective_user.id, coordinates)
        else:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_driver_message.message_id,
                                          text=loading_driver_enabling_search[temp_driver_enabling_search_counter],
                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                              "Sichtbarkeit beenden", callback_data="Zurück ins Startmenü")]]))
            temp_driver_enabling_search_counter += 1


def driver_set_destination(update: Update, context: CallbackContext) -> int:
    """Sets the destination of the driver when starting the "driver" functions

        Args:
            update (telegram.Update)
            context (telegram.ext.CallbackContext)

        Returns:
            int: An integer which represents another status
    """

    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}

    if update.message is not None:

        # Using the live_period property and also the user_data storage inside of context helps to check,
        # if the user sent a live location instead a static location message to the bot
        if update.effective_message.location.live_period and context.user_data["already_sent_live_location"] is False:
            # Removing the markup to clean up the chat history
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=context.user_data["last_message_id"],
                                          text="Wohin fährst du? Bitte teile dein Ziel als Standort mit.")

            # Hints that the driver must only turn off the location sharing and that the last sent location
            # will be used
            msg = context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Wohin fährst du? Bitte teile dein Ziel *als Standort* mit.\n"
                     "Um keine Fehler bei der Benutzung zu haben, schalte *davor* bitte deinen Live-Standort aus.\n\n"
                     "Danach startet die Suche automatisch mit deinem aktuellen Standort.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                    "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]]),
                parse_mode=ParseMode.MARKDOWN
            )

            # Sets up the user_data context storage with necessary data to be able to share them over files and handlers
            context.user_data["last_message_id"] = msg.message_id
            context.user_data["already_sent_live_location"] = True
            # Returns DRIVER_SET_DESTINATION since the user should sent a static location
            return DRIVER_SET_DESTINATION

        # Removing the markup to clean up the chat history
        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                      message_id=context.user_data["last_message_id"],
                                      text="Wohin fährst du? Bitte teile dein Ziel als Standort mit.")

        button_labels = ["Ja", "Nein"]
        button_list = []

        # Makes sure that already_sent_live_location is set to False since we only use a sent static
        # location from the user and not received any live location. It also prevents from any unattractive issue.
        context.user_data["already_sent_live_location"] = False

        for label in button_labels:
            button_list.append(InlineKeyboardButton(label, callback_data=label))

        reply_markup = InlineKeyboardMarkup(
            build_button_menu(button_list, n_cols=1))

        # Sets a sent static location from the user as the destination of his/her travel
        set_driver_destination(update.effective_user.id, coordinates)

        # Sends a message to give written confirmation that the destination was received.
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Danke! Dein Ziel wurde erfasst.\n\n"
                 f"Möchtest du nun für potentielle Mitfahrer sichtbar sein?",
            reply_markup=reply_markup
        )

        return DRIVER_QUERY_HANDLER
