import datetime
from math import radians, cos, sin, asin, sqrt


# TODO: Build Button Menu überall hinzufügen


def haversine(lon1, lat1, lon2, lat2):
    """ Calculate the great circle distance between two points on the earth (specified in decimal degrees)

    Args:
        lon1 (float): The longitude of the first coordinate
        lat1 (float): The latitude of the first coordinate
        lon2 (float): The longitude of the second coordinate
        lat2 (float): The latitude of the second coordinate


    Returns:
        float: Distance between two given coordinates
    """

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def build_button_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    """ Preparing a list for being used in a InlineKeyboardMarkup

    Args:
        buttons (list): The longitude of the first coordinate
        n_cols (int): n_cols = 1 is for single column and other values for multiple rows
        header_buttons: Header Buttons
        footer_buttons: Footer Buttons


    Returns:
        list: Prepared list for the InlineKeyboardMarkup
    """

    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def get_user_age(birthday_str):
    """Returns the rounded off by calculating the difference between the birthday and today

    Args:
        birthday_str (str): The birthday as a string

    Returns:
        float: Rounded age
    """

    birthday = datetime.datetime.strptime(birthday_str, "%d.%m.%Y")

    time_difference = datetime.datetime.today() - birthday

    age = "%.0f" % (time_difference.days / 365)
    return age
