import time

from consts import RADIUS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from main import loading_driver_search
from modules.profile_handler import *
from modules.location_handler import *
from modules.util import build_button_menu

temp_passenger_message = None
temp_driver_search_counter = 2
temp_bool = True


def create_passenger_preparation_menu(update: Update, context: CallbackContext):
    button_labels = ["Ja", "Nein", "Zurück"]
    button_list = []

    for label in button_labels:
        button_list.append(InlineKeyboardButton(label, callback_data=label))

    reply_markup = InlineKeyboardMarkup(
        build_passenger_preparation_menu(button_list, n_cols=1))  # n_cols = 1 is for single column and multiple rows
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Möchtest du deinen aktuellen Standort als Abholpunkt definieren?",
        reply_markup=reply_markup
    )


def build_passenger_preparation_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def passenger_use_current_location(update: Update, context: CallbackContext):
    global temp_passenger_message, temp_driver_search_counter
    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}
    if update.message is not None:
        # Just removes the reply markup
        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                      message_id=context.user_data["last_message_id"],
                                      text="Bitte schicke deinen Live-Standort, damit die Suche nach Fahrern beginnen kann.")

        temp_passenger_message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=loading_driver_search[temp_driver_search_counter - 1],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]])
        )
        set_passenger_current_location(update.effective_user.id, coordinates)
        temp_driver_search_counter = 2  # Resets Search Counter

        # First time check for drivers
        distance_to_drivers = get_distance_from_drivers(coordinates)

        if len(distance_to_drivers) != 0:
            results = []
            for driver in distance_to_drivers:
                if driver["distance"] <= RADIUS:
                    driver_data = get_user_data(driver["user_id"])["data"]
                    driver_data["distance"] = driver["distance"]
                    results.append(driver_data)

            button_list = []

            if len(results) != 0:

                if len(results) == 1:
                    result_text = f"Es wurde {len(results)} Fahrer in deiner Nähe gefunden:"
                else:
                    result_text = f"Es wurdem {len(results)} Fahrer in deiner Nähe gefunden:"

                for data in results:
                    rounded_distance = "%.1f" % data["distance"]
                    callback_data = str({'drv_btn': True, 'uid': data['id'], 'dtc': rounded_distance})
                    label = f"{data['name']} - Distanz: {rounded_distance}km"
                    button_list.append(InlineKeyboardButton(label, callback_data=callback_data))

                button_list.append(
                    InlineKeyboardButton("Zurück ins Startmenü", callback_data="Zurück ins Startmenü"))

                reply_markup = InlineKeyboardMarkup(
                    build_button_menu(button_list, n_cols=1))
                context.user_data["search_result_text"] = result_text
                context.user_data["reply_markup"] = reply_markup
                message_text = loading_driver_search[
                                   temp_driver_search_counter - 1] + f"\n\n{context.user_data['search_result_text']}"
                context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                              message_id=temp_passenger_message.message_id,
                                              text=message_text,
                                              reply_markup=context.user_data["reply_markup"])

            else:
                default_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
                    "Zurück ins Startmenü",
                    callback_data="Zurück ins Startmenü")]])
                context.user_data["search_result_text"] = ""
                # TODO: Push Up Notification - also abkacken angesagt: "Es wurden keine Fahrer gefunden" - danke Gary
                context.user_data["reply_markup"] = default_reply_markup
                message_text = loading_driver_search[temp_driver_search_counter - 1] + f"\n\n{context.user_data['search_result_text']}"
                context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                              message_id=temp_passenger_message.message_id,
                                              text=message_text,
                                              reply_markup=context.user_data["reply_markup"])

    else:
        if temp_driver_search_counter == 2:

            set_passenger_current_location(update.effective_user.id, coordinates)

            distance_to_drivers = get_distance_from_drivers(coordinates)

            if len(distance_to_drivers) != 0:
                results = []
                for driver in distance_to_drivers:
                    if driver["distance"] <= RADIUS:
                        driver_data = get_user_data(driver["user_id"])["data"]
                        driver_data["distance"] = driver["distance"]
                        results.append(driver_data)

                button_list = []

                if len(results) != 0:

                    if len(results) == 1:
                        result_text = f"Es wurde {len(results)} Fahrer in deiner Nähe gefunden:"
                    else:
                        result_text = f"Es wurdem {len(results)} Fahrer in deiner Nähe gefunden:"

                    for data in results:
                        rounded_distance = "%.1f" % data["distance"]
                        callback_data = str({'drv_btn': True, 'uid': data['id'], 'dtc': rounded_distance})
                        label = f"{data['name']} - Distanz: {rounded_distance}km"
                        button_list.append(InlineKeyboardButton(label, callback_data=callback_data))

                    button_list.append(
                        InlineKeyboardButton("Zurück ins Startmenü", callback_data="Zurück ins Startmenü"))

                    reply_markup = InlineKeyboardMarkup(
                        build_button_menu(button_list, n_cols=1))
                    context.user_data["search_result_text"] = result_text
                    context.user_data["reply_markup"] = reply_markup
                    message_text = loading_driver_search[
                                       temp_driver_search_counter] + f"\n\n{context.user_data['search_result_text']}"
                    context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                  message_id=temp_passenger_message.message_id,
                                                  text=message_text,
                                                  reply_markup=context.user_data["reply_markup"])

                else:
                    default_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
                        "Zurück ins Startmenü",
                        callback_data="Zurück ins Startmenü")]])
                    context.user_data["search_result_text"] = ""
                    # TODO: Push Up Notification - also abkacken angesagt: "Es wurden keine Fahrer gefunden" - danke Gary
                    context.user_data["reply_markup"] = default_reply_markup
                    message_text = loading_driver_search[temp_driver_search_counter] + f"\n\n{context.user_data['search_result_text']}"
                    context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                  message_id=temp_passenger_message.message_id,
                                                  text=message_text,
                                                  reply_markup=context.user_data["reply_markup"])

            temp_driver_search_counter = 0
        else:
            message_text = loading_driver_search[
                               temp_driver_search_counter] + f"\n\n{context.user_data['search_result_text']}"
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_passenger_message.message_id,
                                          text=message_text,
                                          reply_markup=context.user_data["reply_markup"])
            temp_driver_search_counter += 1


def passenger_use_other_location(update: Update, context: CallbackContext):
    global temp_passenger_message, temp_driver_search_counter
    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}

    context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                  message_id=context.user_data["last_message_id"],
                                  text="Bitte schicke einen Standort deiner Wahl, damit die Suche nach Fahrern beginnen kann.")

    set_passenger_current_location(update.effective_user.id, coordinates)

    temp_passenger_message = context.bot.send_message(chat_id=update.effective_chat.id,
                                                      text=loading_driver_search[temp_driver_search_counter],
                                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                          "Zurück ins Startmenü",
                                                          callback_data="Zurück ins Startmenü")]]))

    distance_to_drivers = get_distance_from_drivers(coordinates)
    if len(distance_to_drivers) != 0:
        results = []
        for driver in distance_to_drivers:
            if driver["distance"] <= RADIUS:
                driver_data = get_user_data(driver["user_id"])["data"]
                driver_data["distance"] = driver["distance"]
                results.append(driver_data)

        button_list = []

        if len(results) != 0:

            if len(results) == 1:
                result_text = f"Es wurde {len(results)} Fahrer in deiner Nähe gefunden:"
            else:
                result_text = f"Es wurdem {len(results)} Fahrer in deiner Nähe gefunden:"

            if temp_driver_search_counter == 2:
                new_text = loading_driver_search[temp_driver_search_counter] + f"\n\n{result_text}"
                temp_driver_search_counter = 0
            else:
                new_text = loading_driver_search[temp_driver_search_counter] + f"\n\n{result_text}"
                temp_driver_search_counter += 1

            for data in results:
                rounded_distance = "%.1f" % data["distance"]
                callback_data = str({'drv_btn': True, 'uid': data['id'], 'dtc': rounded_distance})
                label = f"{data['name']} - Distanz: {rounded_distance}km"
                button_list.append(InlineKeyboardButton(label, callback_data=callback_data))

            button_list.append(InlineKeyboardButton("Zurück ins Startmenü", callback_data="Zurück ins Startmenü"))

            reply_markup = InlineKeyboardMarkup(
                build_button_menu(button_list, n_cols=1))

            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_passenger_message.message_id,
                                          text=new_text,
                                          reply_markup=reply_markup)

    # TODO: Mit "Job" ersetzen
    """
    while temp_bool:
        time.sleep(1)
        if temp_driver_search_counter == 2:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_message.message_id,
                                          text=loading_driver_search[temp_driver_search_counter])
            temp_driver_search_counter = 0
        else:
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=temp_message.message_id,
                                          text=loading_driver_search[temp_driver_search_counter])
            temp_driver_search_counter += 1
    """
