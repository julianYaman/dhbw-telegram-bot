LOGIN_QUERY_HANDLER, ASK_NAME, ASK_BIRTHDAY, ASK_CAR, CONTACT_OPTIONS_MESSAGE_HANDLER, START_MENU_QUERY_HANDLER, \
    PROFILE_OPTIONS_QUERY_HANDLER, CHANGE_NAME, CHANGE_BIRTHDAY, CHANGE_CAR, DRIVER_QUERY_HANDLER, \
    DRIVER_SET_DESTINATION, DRIVER_ENABLE_PASSENGERS_TO_SEARCH, \
    PASSENGER_QUERY_HANDLER, PASSENGER_USE_CURRENT_LOCATION_TO_PICKUP, \
    PASSENGER_USE_OTHER_LOCATION_TO_PICKUP = range(16)

questions = [
    "Wie lautet dein Name als Fahrer/Mitfahrer?",
    "Wie lautet dein Geburtsdatum? (DD.MM.YYYY)",
    "Was fährst du für ein Auto?"
]

loading_driver_search = [
    "Suche weiterhin nach Fahrern.\n\nEine Liste mit Fahrern wird unter dieser Nachricht automatisch angezeigt und aktualisiert.",
    "Suche weiterhin nach Fahrern..\n\nEine Liste mit Fahrern wird unter dieser Nachricht automatisch angezeigt und aktualisiert.",
    "Suche weiterhin nach Fahrern...\n\nEine Liste mit Fahrern wird unter dieser Nachricht automatisch angezeigt und aktualisiert."
]

loading_driver_enabling_search = [
    "Warte auf Kontakt von möglichen Mitfahrern.",
    "Warte auf Kontakt von möglichen Mitfahrern..",
    "Warte auf Kontakt von möglichen Mitfahrern..."
]

RADIUS = 15
