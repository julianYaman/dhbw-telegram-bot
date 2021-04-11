from main import ASK_BIRTHDAY, ASK_CAR, LOGIN_QUERY_HANDLER, CONTACT_OPTIONS_MESSAGE_HANDLER, \
    START_MENU_QUERY_HANDLER, questions, create_start_menu
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from modules.profile_handler import *
from modules.util import build_button_menu
from telegram.ext import CallbackContext
import datetime

registration_data = {
    "id": "",
    "birthday": "",
    "car": "",
    "link": "",
    "name": ""
}


def create_login(update: Update, context: CallbackContext):
    """Creates the welcome message with its menu.

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int - LOGIN_QUERY_HANDLER state
    """

    button_labels = ["Registrieren", "Einloggen"]
    button_list = []

    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    reply_markup = InlineKeyboardMarkup(
        build_button_menu(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Guten Tag {update.effective_user.first_name}, \n'
             f'ich bin deine persönliche Mitfahrzentrale "LikeUber"! \n\n'
             f'Um die Mitfahrzentrale nutzen zu können, musst du dich vorerst registrieren oder einloggen. \n\n',
        reply_markup=reply_markup
    )

    return LOGIN_QUERY_HANDLER


def ask_name(update: Update, context: CallbackContext):
    """Set the "name" value in the registration object when the name was sent
    (called as the callback for a MessageHandler). Asks then for the birthday of the user and also returns
    the specific state.

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int - ASK_BIRTHDAY state
    """

    global registration_data
    registration_data["name"] = update.message.text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[1]
    )

    return ASK_BIRTHDAY


def ask_birthday(update: Update, context: CallbackContext):
    """Set the "birthday" value in the registration object when the birthday was sent in the registration
    (called as the callback for a MessageHandler). Asks then for the car of the user and also returns
    the specific state. It also checks if the given date has the right format and will return the same question if not.

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int - ASK_CAR state (or, if the date has the wrong format, ASK_BIRTHDAY)
    """

    global registration_data
    date_format = "%d.%m.%Y"
    try:

        datetime.datetime.strptime(update.message.text, date_format)

        registration_data["birthday"] = update.message.text

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=questions[2]
        )

        return ASK_CAR

    except ValueError:

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Dein Datum hat leider das falsche Format.\n\n" + questions[1]
        )

        return ASK_BIRTHDAY


def ask_car(update: Update, context: CallbackContext):
    """Set the "car" value in the registration object when the car was sent in the registration process
    (called as the callback for a MessageHandler). If the user has a username, it will just finish the registration and
    then start directly into the start menu. If the user has no username and just registered with the phone number on
    Telegram, it will ask for it by using KeyboardButtons. The user can cancel the registration at this point.

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int - START_MENU_QUERY_HANDLER state (or, if the user has no username , CONTACT_OPTIONS_MESSAGE_HANDLER)
    """

    global registration_data
    registration_data["car"] = update.message.text
    registration_data["id"] = update.effective_user.id

    # Check if user has a username
    if update.effective_user.link is None:
        contact_options_keyboard = [[KeyboardButton(text="Meine Nummer senden", request_contact=True)],
                                    [KeyboardButton(text="Abbrechen")]]

        reply_markup = ReplyKeyboardMarkup(contact_options_keyboard, resize_keyboard=True, one_time_keyboard=True)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Du hast anscheinend keinen Username in Telegram gesetzt.\n\n"
                 "Du musst dann deine Telefonnummer als Kontaktmöglichkeit angeben um den Bot zu nutzen.\n"
                 "Wenn du das tun möchtest, sende bitte deine Nummer.",
            reply_markup=reply_markup
        )

        context.user_data["registration_data"] = registration_data

        return CONTACT_OPTIONS_MESSAGE_HANDLER

    registration_data["contact_type"] = "dm_link"
    registration_data["link"] = update.effective_user.link

    # Register user with error handling
    register_user_response = register_user(registration_data)
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
