# Used to give every query handler return a specific int value
LOGIN_QUERY_HANDLER, ASK_NAME, ASK_BIRTHDAY, ASK_CAR, CONTACT_OPTIONS_MESSAGE_HANDLER, START_MENU_QUERY_HANDLER, \
    PROFILE_OPTIONS_QUERY_HANDLER, CHANGE_NAME, CHANGE_BIRTHDAY, CHANGE_CAR, DRIVER_QUERY_HANDLER, \
    DRIVER_SET_DESTINATION, DRIVER_ENABLE_PASSENGERS_TO_SEARCH, \
    PASSENGER_QUERY_HANDLER, PASSENGER_USE_CURRENT_LOCATION_TO_PICKUP, \
    PASSENGER_USE_OTHER_LOCATION_TO_PICKUP = range(16)

# Defines all the questions for the registration
questions = [
    "Wie lautet dein Name als Fahrer/Mitfahrer?",
    "Wie lautet dein Geburtsdatum? (DD.MM.YYYY)",
    "Was fährst du für ein Auto?"
]

# Used to animate the driver search
loading_driver_search = [
    "Suche weiterhin nach Fahrern.\n\nEine Liste mit Fahrern wird unter dieser Nachricht automatisch angezeigt und aktualisiert.",
    "Suche weiterhin nach Fahrern..\n\nEine Liste mit Fahrern wird unter dieser Nachricht automatisch angezeigt und aktualisiert.",
    "Suche weiterhin nach Fahrern...\n\nEine Liste mit Fahrern wird unter dieser Nachricht automatisch angezeigt und aktualisiert."
]

# Used to animate a search text while the driver waits for a passenger to contact
loading_driver_enabling_search = [
    "Warte auf Kontakt von möglichen Mitfahrern.",
    "Warte auf Kontakt von möglichen Mitfahrern..",
    "Warte auf Kontakt von möglichen Mitfahrern..."
]

# Defines the radius that is used to limit list of drivers while a passenger is searching for drivers
RADIUS = 15
