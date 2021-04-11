from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from modules.util import build_button_menu


def create_start_menu(update: Update, context: CallbackContext):
    """Creates the start menu which the user can use to proceed after logging in or coming back from using a feature.
    With it, the user can decide to proceed as a driver, as a passenger, updating their data or to log out and ending
    the ConversationHandler

    Args:
        update (telegram.Update)
        context (telegram.ext.CallbackContext)

    Returns:
        None
    """

    button_labels = ["Fahrer", "Mitfahrer", "Profil-Einstellungen", "Abmelden"]
    button_list = []

    # Preparing and appending all buttons for being used in a InlineKeyboardMarkup
    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    # Building the menu with the modules.util build_button_menu function
    reply_markup = InlineKeyboardMarkup(
        build_button_menu(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows

    # Sending the start menu with InlineKeyboardButtons
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Startmenü",
        reply_markup=reply_markup
    )
