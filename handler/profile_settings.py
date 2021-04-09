from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from handler.profile_handler import *
from telegram.ext import CallbackContext
from main import PROFILE_OPTIONS_QUERY_HANDLER


def create_profile_options(update: Update, context: CallbackContext):
    button_labels = ["Name ändern", "Geburtsdatum ändern", "Auto ändern", "Zurück"]
    button_list = []

    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    reply_markup = InlineKeyboardMarkup(build_profile_options(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Profil-Einstellungen",
        reply_markup=reply_markup
    )


def build_profile_options(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def change_name(update: Update, context: CallbackContext):
    update_name_response = update_name(update.effective_user.id, update.message.text)
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
    update_birthday_response = update_birthday(update.effective_user.id, update.message.text)
    if update_birthday_response["error"] is True:
        if update_birthday_response["type"] == "UserNotFound":
            update.message.reply_text("Leider wurde kein User mit deinem Namen gefunden. Bitte registriere dich, um den"
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


def change_car(update: Update, context: CallbackContext):
    update_car_response = update_car(update.effective_user.id, update.message.text)
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
