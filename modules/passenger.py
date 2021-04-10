import time

from consts import RADIUS, PASSENGER_USE_CURRENT_LOCATION_TO_PICKUP, PASSENGER_USE_OTHER_LOCATION_TO_PICKUP
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, JobQueue
from main import loading_driver_search
from modules.profile_handler import *
from modules.location_handler import *
from modules.util import build_button_menu

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
    global temp_driver_search_counter
    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}

    if update.message is not None:
        if update.effective_message.location.live_period is None:
            # Just removes the reply markup
            context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                          message_id=context.user_data["last_message_id"],
                                          text="Bitte schicke deinen Live-Standort, damit die Suche nach Fahrern beginnen kann.")
            msg = context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Bitte schicke *deinen Live-Standort*, damit die Suche nach Fahrern beginnen kann.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                    "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]]),
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["show_drivers_list"] = True
            context.user_data["last_message_id"] = msg.message_id
            return PASSENGER_USE_CURRENT_LOCATION_TO_PICKUP

        # Just removes the reply markup
        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                      message_id=context.user_data["last_message_id"],
                                      text="Bitte schicke deinen Live-Standort, damit die Suche nach Fahrern beginnen kann.")

        temp_driver_search_counter = 2  # Resets Search Counter

        default_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
            "Suche abbrechen", callback_data="Zurück ins Startmenü")]])

        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=loading_driver_search[temp_driver_search_counter - 2],
            reply_markup=default_reply_markup
        )

        context.user_data["passenger_message_id"] = msg.message_id
        context.user_data["show_drivers_list"] = True

        set_passenger_current_location(update.effective_user.id, coordinates)

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
                    result_text = f"Es wurden {len(results)} Fahrer in deiner Nähe gefunden:"

                for data in results:
                    rounded_distance = "%.1f" % data["distance"]
                    callback_data = str({'drv_btn': True, 'uid': data['id'], 'dtc': rounded_distance})
                    label = f"{data['name']} - Distanz: {rounded_distance}km"
                    button_list.append(InlineKeyboardButton(label, callback_data=callback_data))

                button_list.append(
                    InlineKeyboardButton("Suche abbrechen", callback_data="Zurück ins Startmenü"))

                reply_markup = InlineKeyboardMarkup(
                    build_button_menu(button_list, n_cols=1))
                context.user_data["search_result_text"] = result_text
                context.user_data["reply_markup"] = reply_markup

                message_text = loading_driver_search[
                                   temp_driver_search_counter - 1] + f"\n\n{context.user_data['search_result_text']}"
                context.user_data["full_text"] = message_text

                if context.user_data["show_drivers_list"]:
                    context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                  message_id=context.user_data["passenger_message_id"],
                                                  text=message_text,
                                                  reply_markup=context.user_data["reply_markup"])

            else:
                default_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
                    "Suche abbrechen",
                    callback_data="Zurück ins Startmenü")]])

                context.user_data["search_result_text"] = ""
                context.bot.answer_callback_query(context.user_data["query_id"],
                                                  "Es wurden noch keine Fahrer in der Nähe gefunden, die Suche läuft automatisch.",
                                                  show_alert=True)

                context.user_data["reply_markup"] = default_reply_markup

                message_text = loading_driver_search[
                                   temp_driver_search_counter - 1] + f"\n\n{context.user_data['search_result_text']}"
                context.user_data["full_text"] = message_text

                if context.user_data["show_drivers_list"]:
                    context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                  message_id=context.user_data["passenger_message_id"],
                                                  text=message_text,
                                                  reply_markup=context.user_data["reply_markup"])

        else:
            default_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
                "Suche abbrechen",
                callback_data="Zurück ins Startmenü")]])

            context.user_data["search_result_text"] = ""
            context.bot.answer_callback_query(context.user_data["query_id"],
                                              "Es wurden noch keine Fahrer in der Nähe gefunden, die Suche läuft automatisch.",
                                              show_alert=True)

            context.user_data["reply_markup"] = default_reply_markup

            message_text = loading_driver_search[
                               temp_driver_search_counter - 1] + f"\n\n{context.user_data['search_result_text']}"
            context.user_data["full_text"] = message_text

            if context.user_data["show_drivers_list"]:
                context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                              message_id=context.user_data["passenger_message_id"],
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
                        result_text = f"Es wurden {len(results)} Fahrer in deiner Nähe gefunden:"

                    for data in results:
                        rounded_distance = "%.1f" % data["distance"]
                        callback_data = str({'drv_btn': True, 'uid': data['id'], 'dtc': rounded_distance})
                        label = f"{data['name']} - Distanz: {rounded_distance}km"
                        button_list.append(InlineKeyboardButton(label, callback_data=callback_data))

                    button_list.append(
                        InlineKeyboardButton("Suche abbrechen", callback_data="Zurück ins Startmenü"))

                    reply_markup = InlineKeyboardMarkup(
                        build_button_menu(button_list, n_cols=1))
                    context.user_data["search_result_text"] = result_text
                    context.user_data["reply_markup"] = reply_markup

                    message_text = loading_driver_search[
                                       temp_driver_search_counter] + f"\n\n{context.user_data['search_result_text']}"
                    context.user_data["full_text"] = message_text

                    if context.user_data["show_drivers_list"]:
                        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                      message_id=context.user_data["passenger_message_id"],
                                                      text=message_text,
                                                      reply_markup=context.user_data["reply_markup"])

                else:
                    default_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
                        "Suche abbrechen",
                        callback_data="Zurück ins Startmenü")]])
                    context.user_data["search_result_text"] = ""

                    context.user_data["reply_markup"] = default_reply_markup

                    message_text = loading_driver_search[
                                       temp_driver_search_counter] + f"\n\n{context.user_data['search_result_text']}"
                    context.user_data["full_text"] = message_text

                    if context.user_data["show_drivers_list"]:
                        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                      message_id=context.user_data["passenger_message_id"],
                                                      text=message_text,
                                                      reply_markup=context.user_data["reply_markup"])

            else:
                default_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
                    "Suche abbrechen",
                    callback_data="Zurück ins Startmenü")]])

                context.user_data["search_result_text"] = ""

                context.user_data["reply_markup"] = default_reply_markup

                message_text = loading_driver_search[
                                   temp_driver_search_counter] + f"\n\n{context.user_data['search_result_text']}"
                context.user_data["full_text"] = message_text

                if context.user_data["show_drivers_list"]:
                    context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                                  message_id=context.user_data["passenger_message_id"],
                                                  text=message_text,
                                                  reply_markup=context.user_data["reply_markup"])

            temp_driver_search_counter = 0
        else:

            message_text = loading_driver_search[
                               temp_driver_search_counter] + f"\n\n{context.user_data['search_result_text']}"

            if context.user_data["show_drivers_list"]:
                context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                              message_id=context.user_data["passenger_message_id"],
                                              text=message_text,
                                              reply_markup=context.user_data["reply_markup"])
            temp_driver_search_counter += 1


def passenger_use_other_location(update: Update, context: CallbackContext):
    global temp_driver_search_counter
    temp_driver_search_counter = 2  # Resets Search Counter

    coordinates = {"longitude": update.effective_message.location.longitude,
                   "latitude": update.effective_message.location.latitude}

    if update.effective_message.location.live_period and context.user_data["already_sent_live_location"] is False:
        context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                      message_id=context.user_data["last_message_id"],
                                      text="Bitte schicke einen Standort deiner Wahl, damit die Suche nach Fahrern beginnen kann.")
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bitte *schicke einen Standort deiner Wahl*, damit die Suche nach Fahrern beginnen kann.\n"
                 "Um keine Fehler bei der Benutzung zu haben, schalte *davor* bitte deinen Live-Standort aus.\n\n"
                 "Danach startet die Suche automatisch mit deinem aktuellen Standort.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "Zurück ins Startmenü", callback_data="Zurück ins Startmenü")]]),
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data["last_message_id"] = msg.message_id
        context.user_data["already_sent_live_location"] = True
        return PASSENGER_USE_OTHER_LOCATION_TO_PICKUP

    # Edit previous message
    context.bot.edit_message_text(chat_id=update.effective_chat.id,
                                  message_id=context.user_data["last_message_id"],
                                  text="Bitte schicke einen Standort deiner Wahl, damit die Suche nach Fahrern beginnen kann.")

    context.user_data["already_sent_live_location"] = False

    set_passenger_current_location(update.effective_user.id, coordinates)

    msg = context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=loading_driver_search[temp_driver_search_counter - 1])

    context.user_data["passenger_message_id"] = msg.message_id
    context.user_data["static_location"] = coordinates
    context.user_data["show_drivers_list"] = True
    context.user_data["full_text"] = "Suche weiterhin nach Fahrern...\n\nEine Liste mit Fahrern wird " \
                                     "unter dieser Nachricht automatisch angezeigt und aktualisiert."

    context.job_queue.run_repeating(search_for_drivers, 1.5, context=update.effective_chat.id)


def search_for_drivers(context):
    global temp_driver_search_counter
    coordinates = context.dispatcher.user_data[context.job.context]["static_location"]

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
                result_text = f"Es wurden {len(results)} Fahrer in deiner Nähe gefunden:"

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

            button_list.append(InlineKeyboardButton("Suche abbrechen", callback_data="Zurück ins Startmenü"))

            reply_markup = InlineKeyboardMarkup(
                build_button_menu(button_list, n_cols=1))

            # Driver list
            if context.dispatcher.user_data[context.job.context]["show_drivers_list"]:
                context.bot.edit_message_text(chat_id=context.job.context,
                                              message_id=context.dispatcher.user_data[context.job.context]["passenger_message_id"],
                                              text=new_text,
                                              reply_markup=reply_markup)

    else:
        default_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(
            "Suche abbrechen",
            callback_data="Zurück ins Startmenü")]])

        context.dispatcher.user_data[context.job.context]["search_result_text"] = "Es wurden noch keine Fahrer in der Nähe gefunden."

        context.dispatcher.user_data[context.job.context]["reply_markup"] = default_reply_markup

        if temp_driver_search_counter == 2:
            message_text = loading_driver_search[
                               temp_driver_search_counter] + f"\n\n{context.dispatcher.user_data[context.job.context]['search_result_text']}"
            temp_driver_search_counter = 0
        else:
            message_text = loading_driver_search[
                               temp_driver_search_counter] + f"\n\n{context.dispatcher.user_data[context.job.context]['search_result_text']}"
            temp_driver_search_counter += 1

        if context.dispatcher.user_data[context.job.context]["show_drivers_list"]:
            context.bot.edit_message_text(chat_id=context.job.context,
                                          message_id=context.dispatcher.user_data[context.job.context]["passenger_message_id"],
                                          text=message_text,
                                          reply_markup=context.dispatcher.user_data[context.job.context]["reply_markup"])
