import json


def set_driver_current_location(user_id, coordinates):
    with open('data/location.json', 'r') as location_collection:
        try:
            data = json.load(location_collection)
            for location_dataset in data:
                if location_dataset["user_id"] == user_id and location_dataset["is_current_location"]:
                    location_dataset["coordinates"] = coordinates
                    with open('data/location.json', 'w') as file:
                        try:
                            json.dump(data, file, sort_keys=True, indent=4)
                            return {"error": False, "type": "UpdateLocationSuccess"}
                        except:
                            print("Error occurred when trying to open the file location.json")
                            return {"error": True, "type": "JSONFileError"}

            with open('data/location.json', 'w') as file:

                try:
                    new_dataset = {"user_id": user_id, "driver": True, "passenger": False,
                                   "coordinates": coordinates, "is_current_location": True, "is_destination": False}

                    data.append(new_dataset)
                    json.dump(data, file, sort_keys=True, indent=4)

                    return {"error": False, "type": "SetLocationSuccess"}
                except:
                    print("Error occurred when trying to open the file location.json")
                    return {"error": True, "type": "JSONFileError"}
        except:
            print("Error occurred when trying to open the file location.json")
            return {"error": True, "type": "JSONFileError"}


def set_driver_destination(user_id, coordinates):
    with open('data/location.json', 'r') as location_collection:
        try:
            data = json.load(location_collection)
            for location_dataset in data:
                if location_dataset["user_id"] == user_id  and location_dataset["is_destination"]:
                    with open('data/location.json', 'w') as file:
                        try:
                            location_dataset["coordinates"] = coordinates
                            json.dump(data, file, sort_keys=True, indent=4)
                            return {"error": False, "type": "UpdateDestinationSuccess"}
                        except:
                            print("Error occurred when trying to open the file location.json")
                            return {"error": True, "type": "JSONFileError"}

            with open('data/location.json', 'w') as file:

                try:
                    new_dataset = {"user_id": user_id, "driver": True, "passenger": False,
                                   "coordinates": coordinates, "is_current_location": False, "is_destination": True}

                    data.append(new_dataset)
                    json.dump(data, file, sort_keys=True, indent=4)

                    return {"error": False, "type": "SetDestinationSuccess"}
                except:
                    print("Error occurred when trying to open the file location.json")
                    return {"error": True, "type": "JSONFileError"}
        except:
            print("Error occurred when trying to open the file location.json")
            return {"error": True, "type": "JSONFileError"}


def delete_driver_data(user_id):
    with open('data/location.json', 'r') as location_collection:
        try:
            data = json.load(location_collection)
            new_data = []
            for location_dataset in data:
                if location_dataset["user_id"] != user_id:
                    new_data.append(location_dataset)
            data = new_data
            with open('data/location.json', 'w') as file:
                try:
                    json.dump(data, file, sort_keys=True, indent=4)
                except:
                    print("Error occurred when trying to open the file location.json")
                    return {"error": True, "type": "JSONFileError"}
            return {"error": False, "type": "NoDataFound"}
        except:
            print("Error occurred when trying to open the file location.json")
            return {"error": True, "type": "JSONFileError"}
