import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from modules.profile_handler import *
from modules.util import *
from telegram.ext import CallbackContext
from main import PROFILE_OPTIONS_QUERY_HANDLER, CHANGE_BIRTHDAY


def create_profile_options(update: Update, context: CallbackContext):
    """Creates the menu for the profile options feature

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        None
    """

    button_labels = ["Name ändern", "Geburtsdatum ändern", "Auto ändern", "Zurück"]
    button_list = []

    # Preparing and appending all buttons for being used in a InlineKeyboardMarkup
    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    # Building the menu with the modules.util build_button_menu function
    reply_markup = InlineKeyboardMarkup(build_button_menu(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows

    # Sending the profile options menu with InlineKeyboardButtons
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Profil-Einstellungen",
        reply_markup=reply_markup
    )


def change_name(update: Update, context: CallbackContext):
    """Sets the new name of the user (called as the callback for a MessageHandler)

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int - PROFILE_OPTIONS_QUERY_HANDLER state
    """

    update_name_response = update_name(update.effective_user.id, update.message.text)
    # Error handling
    if update_name_response["error"] is True:
        if update_name_response["type"] == "UserNotFound":
            update.message.reply_text("Leider wurde kein User mit deinem Namen gefunden. Bitte registriere dich, um den"
                                      " Bot nutzen zu können")
            create_profile_options(update, context)
        elif update_name_response["type"] == "JSONFileError":
            update.message.reply_text("Leider ist ein Fehler beim Aufrufen der Daten aufgetreten.")
            create_profile_options(update, context)
        else:
            update.message.reply_text("Ein unbekannter Fehler ist aufgetreten.")
            create_profile_options(update, context)
    else:
        if update_name_response["type"] == "UpdatedName":
            update.message.reply_text(f"Du hast deinen Namen erfolgreich in {update.message.text} geändert")
            create_profile_options(update, context)

    return PROFILE_OPTIONS_QUERY_HANDLER


def change_birthday(update: Update, context: CallbackContext):
    """Sets a new birthday for the user (called as the callback for a MessageHandler).
    Also checks if the date format is right.

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int - PROFILE_OPTIONS_QUERY_HANDLER state
    """
    # Define specific date format for further operations
    date_format = "%d.%m.%Y"

    try:
        datetime.datetime.strptime(update.message.text, date_format)
        update_birthday_response = update_birthday(update.effective_user.id, update.message.text)
        # Error handling
        if update_birthday_response["error"] is True:
            if update_birthday_response["type"] == "UserNotFound":
                update.message.reply_text(
                    "Leider wurde kein User mit deinem Namen gefunden. Bitte registriere dich, um den"
                    " Bot nutzen zu können")
                create_profile_options(update, context)
            elif update_birthday_response["type"] == "JSONFileError":
                update.message.reply_text("Leider ist ein Fehler beim Aufrufen der Daten aufgetreten.")
                create_profile_options(update, context)
            else:
                update.message.reply_text("Ein unbekannter Fehler ist aufgetreten.")
                create_profile_options(update, context)
        else:
            if update_birthday_response["type"] == "UpdatedBirthday":
                update.message.reply_text(f"Dein Geburtsdatum ist nun der {update.message.text}")
                create_profile_options(update, context)

        return PROFILE_OPTIONS_QUERY_HANDLER

    except ValueError:

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Dein Datum hat leider das falsche Format.\n\n"
        )

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Wann wurdest du geboren? (DD.MM.YYYY)"
        )
        return CHANGE_BIRTHDAY


def change_car(update: Update, context: CallbackContext):
    """Sets a new car for the user (called as the callback for a MessageHandler).

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        int - PROFILE_OPTIONS_QUERY_HANDLER state
    """

    update_car_response = update_car(update.effective_user.id, update.message.text)
    # Error handling
    if update_car_response["error"] is True:
        if update_car_response["type"] == "UserNotFound":
            update.message.reply_text("Leider wurde kein User mit deinem Namen gefunden. Bitte registriere dich, um den"
                                      " Bot nutzen zu können")
            create_profile_options(update, context)
        elif update_car_response["type"] == "JSONFileError":
            update.message.reply_text("Leider ist ein Fehler beim Aufrufen der Daten aufgetreten.")
            create_profile_options(update, context)
        else:
            update.message.reply_text("Ein unbekannter Fehler ist aufgetreten.")
            create_profile_options(update, context)
    else:
        if update_car_response["type"] == "UpdatedCar":
            update.message.reply_text(f"Du hast dein Auto zu \"{update.message.text}\" geändert")
            create_profile_options(update, context)

    return PROFILE_OPTIONS_QUERY_HANDLER
