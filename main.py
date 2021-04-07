from telegram import Update
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
    bot = Updater(token='1783162081:AAGSSI5KySI1xb1wXRmIte-x58sBR9DzbO4', use_context=True)

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
