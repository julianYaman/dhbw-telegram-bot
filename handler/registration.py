from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from handler.profile_handler import *
from telegram.ext import CallbackContext
from main import ASK_BIRTHDAY, ASK_CAR, LOGIN_QUERY_HANDLER, questions, create_start_menu

registration_data = {
    "id": "",
    "birthday": "",
    "car": "",
    "link": "",
    "name": ""
}


def create_login(update: Update, context: CallbackContext):
    button_labels = ["Registrieren", "Einloggen"]
    button_list = []

    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    reply_markup = InlineKeyboardMarkup(
        build_login(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Guten Tag {update.effective_user.first_name}, \n'
             f'ich bin deine persönliche Mitfahrzentrale "likeuber"! \n\n'
             f'Um die Mitfahrzentrale nutzen zu können, musst du dich vorerst registrieren oder einloggen. \n\n',
        reply_markup=reply_markup
    )

    return LOGIN_QUERY_HANDLER


def build_login(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def ask_name(update: Update, context: CallbackContext):
    global registration_data
    registration_data["name"] = update.message.text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[1]
    )

    return ASK_BIRTHDAY


def ask_birthday(update: Update, context: CallbackContext):
    global registration_data
    registration_data["birthday"] = update.message.text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=questions[2]
    )

    return ASK_CAR


def ask_car(update: Update, context: CallbackContext):
    global registration_data
    registration_data["car"] = update.message.text

    complete_registration(update, context)


def complete_registration(update: Update, context: CallbackContext):
    global registration_data
    registration_data["id"] = update.effective_user.id
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
            )
            create_start_menu(update, context)
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Keine Ahnung was passiert ist, aber es hat funktioniert."
            )
