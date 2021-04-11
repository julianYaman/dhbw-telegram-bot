import json


def login_user(user):
    """Authenticate the user with a login

    Args:
        user (dict) - The user object

    Returns:
        dict: Returns a success object containing the information if the login was successful
    """

    data = None

    with open("data/users.json", "r") as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user["id"]:
                    return {"error": False, "type": "UserFound", "name": saved_user["name"]}
            return {"error": True, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def register_user(user):
    """Creates a new user via registration

    Args:
        user (dict) - The registration object for creating a new entry

    Returns:
        dict: Returns a success object containing the information if the registration was successful
    """

    data = None

    with open("data/users.json", "r") as user_collection_file:
        try:
            data = json.load(user_collection_file)
        except:
            return {"error": True, "type": "JSONFileError"}

        for saved_user in data:
            if saved_user["id"] == user["id"]:
                return {"error": True, "type": "AlreadyRegistered"}

    with open("data/users.json", "w") as user_collection_file:
        try:
            new_user = {"id": user["id"], "birthday": user["birthday"], "car": user["car"], "link": user["link"],
                        "name": user["name"], "contact_type": user["contact_type"]}

            data.append(new_user)
            json.dump(data, user_collection_file, sort_keys=True, indent=4)

            return {"error": False, "type": "SuccessfullyRegistered"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def is_already_registered(user_id):
    """Checks if the user does already exists

    Args:
        user_id (int) - The ID of the user

    Returns:
        dict: Returns a object if the user does exist or not
    """

    data = None

    with open("data/users.json", "r") as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user_id:
                    return {"error": False, "type": "UserFound", "name": saved_user["name"]}
            return {"error": False, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def get_user_data(user_id):
    """Gets the data of the user from the users storage file

    Args:
        user_id (int) - The ID of the user

    Returns:
        dict: Returns a success object which will contain the user data if the user was found
    """

    data = None

    with open("data/users.json", "r") as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user_id:
                    return {"error": False, "type": "UserFound", "data": saved_user}
            return {"error": True, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def get_user_contact_type(user_id):
    """Gets the main contact type of the user

    Args:
        user_id (int) - The ID of the user

    Returns:
        dict: Returns a success object which will contain the contact type if the user was found
    """

    data = None

    with open("data/users.json", "r") as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user_id:
                    return {"error": False, "type": "UserFound", "contact_type": saved_user["contact_type"]}
            return {"error": True, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def get_user_contact_value(user_id):
    """Gets the Telegram chat link or the phone number, depending of the type of contact the user registered with

    Args:
        user_id (int) - The ID of the user

    Returns:
        dict: Returns a success object which will contain the contact details if the user was found
    """

    data = None

    with open("data/users.json", "r") as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user_id:
                    return {"error": False, "type": "UserFound", "link": saved_user["link"]}
            return {"error": True, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def update_name(user_id, name):
    """Updates the name of a user in the user storage file if the user exists

    Args:
        user_id (int) - The ID of the user
        name (str) - The new name

    Returns:
        dict: Returns a success object containing the information if the action was successful
    """

    data = None

    with open("data/users.json", "r") as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user_id:
                    with open("data/users.json", "w") as file:
                        try:
                            saved_user["name"] = name
                            json.dump(data, file, sort_keys=True, indent=4)
                            return {"error": False, "type": "UpdatedName"}
                        except:
                            print("Error occurred when trying to open the file users.json")
                            return {"error": True, "type": "JSONFileError"}
            return {"error": True, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def update_birthday(user_id, birthday):
    """Updates the birthday of a user in the user storage file if the user exists

    Args:
        user_id (int) - The ID of the user
        birthday (str) - The new name

    Returns:
        dict: Returns a success object containing the information if the action was successful
    """

    data = None

    with open("data/users.json", "r") as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user_id:
                    with open("data/users.json", "w") as file:
                        try:
                            saved_user["birthday"] = birthday
                            json.dump(data, file, sort_keys=True, indent=4)
                            return {"error": False, "type": "UpdatedBirthday"}
                        except:
                            print("Error occurred when trying to open the file users.json")
                            return {"error": True, "type": "JSONFileError"}
            return {"error": True, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def update_car(user_id, car):
    """Updates the car of a user in the user storage file if the user exists

    Args:
        user_id (int) - The ID of the user
        car (str) - The new car

    Returns:
        dict: Returns a success object containing the information if the action was successful
    """

    data = None

    with open("data/users.json", "r") as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user_id:
                    with open("data/users.json", "w") as file:
                        try:
                            saved_user["car"] = car
                            json.dump(data, file, sort_keys=True, indent=4)
                            return {"error": False, "type": "UpdatedCar"}
                        except:
                            print("Error occurred when trying to open the file users.json")
                            return {"error": True, "type": "JSONFileError"}
            return {"error": True, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}
