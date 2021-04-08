from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from handler.profile_handler import *
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler

bot = None
START_QUERY_HANDLER, ASK_NAME, ASK_BIRTHDAY, ASK_CAR = range(4)  # Just some placeholders

questions = [
    "Wie lautet dein Name als Fahrer/Mitfahrer?",
    "Wie lautet dein Geburtsdatum? (DD.MM.YYYY)",
    "Was fährst du für ein Auto?"
]

question_counter = 0

registration_data = {
    "id": "",
    "birthday": "",
    "car": "",
    "link": "",
    "name": ""
}


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


def create_login(update: Update, context: CallbackContext):
  button_labels = ["Registrieren", "Einloggen"]
  button_list = []

  for label in button_labels:
     button_list.append(InlineKeyboardButton(label, callback_data=label))

  reply_markup = InlineKeyboardMarkup(build_login(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows
  context.bot.send_message(
      chat_id=update.effective_chat.id,
      text=f'Guten Tag {update.effective_user.first_name}, \n'
           f'ich bin deine persönliche Mitfahrzentrale "likeuber"! \n\n'
           f'Um die Mitfahrzentrale nutzen zu können, musst du dich vorerst registrieren oder einloggen. \n\n',
      reply_markup=reply_markup
  )

  return START_QUERY_HANDLER


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


def create_start_menu(update: Update, context: CallbackContext):
    button_labels = ["Fahrer", "Mitfahrer", "Profil-Einstellungen"]
    button_list = []

    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    reply_markup = InlineKeyboardMarkup(build_start_menu(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Startmenü",
        reply_markup=reply_markup
    )


def build_start_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def query_handler(update: Update, context: CallbackContext):
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


def cancel(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Bye :-)"
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

    login_handler = ConversationHandler(
        entry_points=[CommandHandler('start', create_login)],
        states={
            START_QUERY_HANDLER: [CallbackQueryHandler(query_handler)],
            ASK_NAME: [MessageHandler(Filters.text, ask_name)],
            ASK_BIRTHDAY: [MessageHandler(Filters.text, ask_birthday)],
            ASK_CAR: [MessageHandler(Filters.text, ask_car)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    bot.dispatcher.add_handler(login_handler)

    bot.idle()


if __name__ == "__main__":
    main()
