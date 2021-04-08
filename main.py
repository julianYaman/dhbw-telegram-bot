from telegram import Update
from handler.profile_handler import *
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

chat_id = ''

questions = [
    "Wie lautet dein Geburtsdatum? (DD.MM.YYYY)",
    "Was fährst du für ein Auto?"
]

question_counter = 0

registration_data = {
    "id": "",
    "birthday": "",
    "car": "",
    "link": "",
    "name": "",
    "traveler": False,
    "driver": False
}

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


def next_question(question_index):
    question = questions[question_index]
    return question


def reply(update, context):
    user_input = update.message.text

    global question_counter
    global registration_data

    if question_counter == 0:
        registration_data["name"] = user_input
    elif question_counter == 1:
        registration_data["birthday"] = user_input
    else:
        registration_data["car"] = user_input

    if question_counter < 2:
        update.message.reply_text(next_question(question_counter))
        question_counter += 1
    else:
        question_counter += 1


def start_chat(update: Update, context: CallbackContext):
    global chat_id
    chat_id = update.message.chat.id

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Guten Tag {update.effective_user.first_name}, \n'
             f'ich bin deine persönliche Mitfahrzentrale "likeuber"! \n\n'
             f'Um die Mitfahrzentrale nutzen zu können, musst du dich vorerst registrieren, dafür benötige ich diverse Daten von dir. \n\n'
             f'Wie lautet dein Name als Fahrer/Mitfahrer?'
    )


def main():
    
    token = None

    with open('data/bot.json', 'r') as config_file:
      try:
          data = json.load(config_file)
          token = data['token']
      except:
          print("Error occurred when trying to open the file bot.json")
          quit()
                                      
    bot = Updater(token=token, use_context=True)

    bot.dispatcher.add_handler(CommandHandler('start', start_chat))

    questions_handler = MessageHandler(Filters.text, reply)

    bot.dispatcher.add_handler(questions_handler)

    bot.start_polling()

    global question_counter
    while question_counter < 4:
        if question_counter == 3:
            bot.dispatcher.remove_handler(questions_handler)
            question_counter += 1

            bot.bot.sendMessage(chat_id=chat_id, text='Danke für deine Registrierung!')
            print(registration_data)

    bot.idle()


if __name__ == "__main__":
    main()
