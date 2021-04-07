import json


def login_user(user):
    data = None

    with open('data/users.json', 'r') as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user.id:
                    return {"error": False, "type": "UserFound", "name": saved_user["name"]}
            return {"error": True, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def register_user(user):
    data = None

    with open('data/users.json', 'r') as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user.id:
                    return {"error": True, "type": "AlreadyRegistered"}
        except:
            return {"error": True, "type": "JSONFileError"}

    with open('data/users.json', 'w') as user_collection_file:
        try:
            new_user = {'id': user.id, 'birthday': None, 'car': None, 'link': user.link,
                        'name': user.full_name, 'traveler': False, 'driver': False}

            data.append(new_user)
            json.dump(data, user_collection_file)

            return {"error": False, "type": "SuccessfullyRegistered"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


def update_name(user_id, name):
    data = None

    with open('data/users.json', 'r') as user_collection_file:
        try:
            data = json.load(user_collection_file)
            for saved_user in data:
                if saved_user["id"] == user_id:
                    with open('data/users.json', 'w') as file:
                        try:
                            saved_user["name"] = name
                            json.dump(data, file)
                            return {"error": False, "type": "UpdatedName"}
                        except:
                            print("Error occurred when trying to open the file users.json")
                            return {"error": True, "type": "JSONFileError"}
            return {"error": True, "type": "UserNotFound"}
        except:
            print("Error occurred when trying to open the file users.json")
            return {"error": True, "type": "JSONFileError"}


