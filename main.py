from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, \
    ConversationHandler
from consts import *
from handler.registration import *
from handler.start_menu import *
from handler.profile_settings import *

bot = None

question_counter = 0


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
                text="Leider wurde kein User mit deinem Namen gefunden. Bitte registriere dich, um den Bot nutzen zu können."
            )
            create_login(update, context)
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
                else:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Keine Ahnung was passiert ist, aber es hat funktioniert."
                    )

    return START_MENU_QUERY_HANDLER


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
        print("Fahrer")
    elif query.data == "Mitfahrer":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
        print("Mitfahrer")
    elif query.data == "Profil-Einstellungen":
        query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))  # Remove inline keyboard from message
        create_profile_options(update, context)

    return PROFILE_OPTIONS_QUERY_HANDLER


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
            START_MENU_QUERY_HANDLER: [CallbackQueryHandler(start_menu_query_handler)],
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
