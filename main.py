from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from handler.profile_handler import *


def login(update: Update, context: CallbackContext) -> None:
    login_user_respone = login_user(update.effective_user)
    if login_user_respone["error"] is True:
        if login_user_respone["type"] == "UserNotFound":
            update.message.reply_text("Leider wurde kein User mit deinem Namen gefunden. Bitte registriere dich, um den"
                                      " Bot nutzen zu können")
        elif login_user_respone["type"] == "JSONFileError":
            update.message.reply_text("Leider ist ein Fehler beim Aufrufen der Daten aufgetreten.")
        else:
            update.message.reply_text("Ein unbekannter Fehler ist aufgetreten.")
    else:
        if login_user_respone["type"] == "UserFound":
            update.message.reply_text(f"Du hast dich erfolgreich eingeloggt! Willkommen zurück, "
                                      f"{login_user_respone['name']}")
            # TODO: Hier weitere User-Aktionen festlegen
        else:
            update.message.reply_text("Keine Ahnung was passiert ist, aber es hat funktioniert.")


def register(update: Update, context: CallbackContext) -> None:
    register_user_response = register_user(update.effective_user)
    if register_user_response["error"] is True:
        if register_user_response["type"] == "AlreadyRegistered":
            update.message.reply_text("Du hast dich bereits registriert. Bitte versuche dich einzuloggen.")
        elif register_user_response["type"] == "JSONFileError":
            update.message.reply_text("Leider ist ein Fehler beim Aufrufen der Daten aufgetreten.")
        else:
            update.message.reply_text("Ein unbekannter Fehler ist aufgetreten.")
    else:
        if register_user_response["type"] == "SuccessfullyRegistered":
            update.message.reply_text("Glückwunsch! Du hast einen neuen Account erstellt.")
            # TODO: Hier weitere User-Aktionen festlegen
        else:
            update.message.reply_text("Keine Ahnung was passiert ist, aber es hat funktioniert.")


def change_name(update: Update, context: CallbackContext) -> None:
    # TODO: Value für neuen Namen abfangen
    update_name_response = update_name(update.effective_user.id, 'Testname')
    if update_name_response["error"] is True:
        if update_name_response["type"] == "UserNotFound":
            update.message.reply_text("Leider wurde kein User mit deinem Namen gefunden. Bitte registriere dich, um den"
                                      " Bot nutzen zu können")
        elif update_name_response["type"] == "JSONFileError":
            update.message.reply_text("Leider ist ein Fehler beim Aufrufen der Daten aufgetreten.")
        else:
            update.message.reply_text("Ein unbekannter Fehler ist aufgetreten.")
    else:
        if update_name_response["type"] == "UpdatedName":
            # TODO: Neuen Usernamen hier einfügen
            update.message.reply_text("Du hast deinen Namen erfolgreich in ... geändert")


# TODO: Ordentliche 'main' Funktion integrieren (s. Tutorials)
token = None

with open('data/bot.json', 'r') as config_file:
    try:
        data = json.load(config_file)
        token = data['token']
    except:
        print("Error occurred when trying to open the file bot.json")

updater = Updater(token)

updater.dispatcher.add_handler(CommandHandler('login', login))
updater.dispatcher.add_handler(CommandHandler('register', register))
updater.dispatcher.add_handler(CommandHandler('changename', change_name))

updater.start_polling()
updater.idle()
