import json
from modules.util import haversine


def get_driver_destination(user_id):
    """Gets the destination of the driver with the given user_id

    Args:
        user_id (int): The ID of the user

    Returns:
        dist: Coordinates dictionary containing the longitude and the latitude of the destination of the driver
    """

    result = None
    # Opens the location data storage file in READ mode and searches for the driver and the related destination object
    # by using a for loop.
    with open('data/location.json', 'r') as location_collection:
        try:
            data = json.load(location_collection)

            for location_dataset in data:
                # If the user has the specified ID, is a driver and has "is_destination" set to True in the
                # current object, then the coordinates of the driver's destination are returned
                if location_dataset["user_id"] == user_id and location_dataset["driver"] and location_dataset["is_destination"]:
                    result = location_dataset["coordinates"]

            return result
        except:
            # If the file could not be opened, it will return an error dictionary with a custom error type
            print("Error occurred when trying to open the file location.json")
            return {"error": True, "type": "JSONFileError"}


def get_distance_from_drivers(coordinates):
    """Returns the result of calculating the distance from one point on a sphere to another in kilometers by using the
    haversine formula

    Args:
        coordinates (dict): The coordinates dictionary containing the longitude and the latitude *of the passenger*

    Returns:
        list: List of dictionaries containing the user_id of the driver and the distance to the driver
    """

    results = []
    # Opens the location data storage file in READ mode and searches for all dateset of
    # drivers with their current location
    with open('data/location.json', 'r') as location_collection:
        try:
            data = json.load(location_collection)

            for location_dataset in data:
                # If the user is a driver and has "is_current_location" set to True,
                # then the coordinates of the passenger and the one of the driver will be used to calculate the distance
                # by using the [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula)
                if location_dataset["driver"] and location_dataset["is_current_location"]:
                    # Calculating the distance - function can be found in modules.util
                    distance = haversine(coordinates["longitude"], coordinates["latitude"],
                                         location_dataset["coordinates"]["longitude"],
                                         location_dataset["coordinates"]["latitude"])

                    # Appends dictionaries to the array list containing all drivers and their distance to the user
                    results.append({"distance": distance, "user_id": location_dataset["user_id"]})

            return results
        except:
            # If the file could not be opened, it will return an error dictionary with a custom error type
            print("Error occurred when trying to open the file location.json")
            return {"error": True, "type": "JSONFileError"}


def set_driver_current_location(user_id, coordinates):
    """Sets and updates the current live location of the driver in the location data storage

    Args:
        user_id (int): The user ID of the driver
        coordinates (dict): The coordinates dictionary containing the longitude and the latitude *of the driver*

    Returns:
        dict: Returns a success object containing the information if the action was successful
    """

    # Opens the location data storage file first in READ mode and then checks if the a "current location" already
    # exists in the JSON file or if a new entry must be made
    with open('data/location.json', 'r') as location_collection:
        try:
            data = json.load(location_collection)

            # Loops through all objects in the array and looking for all drivers
            # of which their live location is currently saved in the file
            for location_dataset in data:
                if location_dataset["user_id"] == user_id and location_dataset["driver"] and \
                        location_dataset["is_current_location"]:

                    # Updating the coordinates value of the key "coordinates" in the local variable
                    location_dataset["coordinates"] = coordinates

                    # Writing into the file with the updated list of location data
                    with open('data/location.json', 'w') as file:
                        try:
                            json.dump(data, file, sort_keys=True, indent=4)
                            return {"error": False, "type": "UpdateLocationSuccess"}
                        except:
                            # If the file could not be opened, it will return an error
                            # dictionary with a custom error type
                            print("Error occurred when trying to open the file location.json")
                            return {"error": True, "type": "JSONFileError"}

            # If no "current location" entry could be found, then a new one will be created by opening the file in
            # WRITE mode and dumping a new dataset into it.
            with open('data/location.json', 'w') as file:

                try:
                    # Creating a new dataset which will then be dumped into the file
                    new_dataset = {"user_id": user_id, "driver": True, "passenger": False,
                                   "coordinates": coordinates, "is_current_location": True, "is_destination": False}

                    data.append(new_dataset)
                    json.dump(data, file, sort_keys=True, indent=4)

                    return {"error": False, "type": "SetLocationSuccess"}
                except:
                    # If the file could not be opened, it will return an error dictionary with a custom error type
                    print("Error occurred when trying to open the file location.json")
                    return {"error": True, "type": "JSONFileError"}
        except:
            # If the file could not be opened, it will return an error dictionary with a custom error type
            print("Error occurred when trying to open the file location.json")
            return {"error": True, "type": "JSONFileError"}


def set_driver_destination(user_id, destination):
    """Sets the destination of a new driver with a given user_id

    Args:
        user_id (int): The ID of the user
        destination (dist): The destination containing the longitude and the latitude of the destination

    Returns:
        dict: Returns a success object containing the information if the action was successful
    """

    # Opens the location data storage file first in READ mode and then checks if there is already a destination
    # (highly unlikely)  in the JSON file or if it needs to create a new destination entry
    with open('data/location.json', 'r') as location_collection:
        try:
            data = json.load(location_collection)

            # Loops through all objects in the array and looking for all drivers
            # of which their destination is currently saved in the file (highly unlikely to happen)
            for location_dataset in data:
                if location_dataset["user_id"] == user_id and location_dataset["driver"] \
                        and location_dataset["is_destination"]:
                    with open('data/location.json', 'w') as file:
                        try:
                            location_dataset["coordinates"] = destination
                            json.dump(data, file, sort_keys=True, indent=4)
                            return {"error": False, "type": "UpdateDestinationSuccess"}
                        except:
                            # If the file could not be opened, it will return an error dictionary with a custom error type
                            print("Error occurred when trying to open the file location.json")
                            return {"error": True, "type": "JSONFileError"}

            # Writing the given destination into the location storage file
            with open('data/location.json', 'w') as file:

                try:
                    # Creating a new destination dataset which will then be dumped into the file
                    new_dataset = {"user_id": user_id, "driver": True, "passenger": False, "coordinates": destination,
                                   "is_current_location": False, "is_destination": True}

                    data.append(new_dataset)
                    json.dump(data, file, sort_keys=True, indent=4)

                    return {"error": False, "type": "SetDestinationSuccess"}
                except:
                    # If the file could not be opened, it will return an error dictionary with a custom error type
                    print("Error occurred when trying to open the file location.json")
                    return {"error": True, "type": "JSONFileError"}
        except:
            # If the file could not be opened, it will return an error dictionary with a custom error type
            print("Error occurred when trying to open the file location.json")
            return {"error": True, "type": "JSONFileError"}


def set_passenger_current_location(user_id, coordinates):
    """Sets or updates the current location of a passenger

    Args:
        user_id (int): The ID of the user
        coordinates (dist): The coordinates containing the longitude and the latitude of the current live location

    Returns:
        dict: Returns a success object containing the information if the action was successful
    """

    # Opens the location data storage file first in READ mode and then checks if there is already a object containing
    # the current live location of the passenger or if a new passenger entry must be added
    with open('data/location.json', 'r') as location_collection:
        try:
            data = json.load(location_collection)

            # Loops through all objects in the array and looking for all passengers
            # of which their live location was already saved in the file
            for location_dataset in data:
                if location_dataset["user_id"] == user_id and location_dataset["passenger"] \
                        and location_dataset["is_current_location"]:

                    # Updating the coordinates value of the key "coordinates" in the local variable
                    location_dataset["coordinates"] = coordinates

                    # Writing into the file with the updated list of location data
                    with open('data/location.json', 'w') as file:
                        try:
                            json.dump(data, file, sort_keys=True, indent=4)
                            return {"error": False, "type": "UpdateLocationSuccess"}
                        except:
                            # If the file could not be opened, it will return an error
                            # dictionary with a custom error type
                            print("Error occurred when trying to open the file location.json")
                            return {"error": True, "type": "JSONFileError"}

            # If no "current location" entry could be found, then a new one will be created by opening the file in
            # WRITE mode and dumping a new dataset into it.
            with open('data/location.json', 'w') as file:

                try:
                    # Creating a new dataset which will then be dumped into the file
                    new_dataset = {"user_id": user_id, "driver": False, "passenger": True,
                                   "coordinates": coordinates, "destination": "",
                                   "is_current_location": True, "is_destination": False}

                    data.append(new_dataset)
                    json.dump(data, file, sort_keys=True, indent=4)

                    return {"error": False, "type": "SetLocationSuccess"}
                except:
                    # If the file could not be opened, it will return an error dictionary with a custom error type
                    print("Error occurred when trying to open the file location.json")
                    return {"error": True, "type": "JSONFileError"}
        except:
            # If the file could not be opened, it will return an error dictionary with a custom error type
            print("Error occurred when trying to open the file location.json")
            return {"error": True, "type": "JSONFileError"}


def delete_user_location_data(user_id):
    """Deletes all the location data saved from a user with the given user ID

    Args:
        user_id (int): The ID of the user

    Returns:
        dict: Returns a success object containing the information if the action was successful
    """
    with open('data/location.json', 'r') as location_collection:
        try:
            data = json.load(location_collection)
            new_data = []

            # Looping through all the data and appending all data which DOES NOT belong to the
            # user with the give user_id
            for location_dataset in data:
                if location_dataset["user_id"] != user_id:
                    # the new list contains all data except the data from the user with the given user_id
                    new_data.append(location_dataset)

            data = new_data

            # Writing the new data list into the location file storage
            with open('data/location.json', 'w') as file:
                try:
                    json.dump(data, file, sort_keys=True, indent=4)
                except:
                    # If the file could not be opened, it will return an error dictionary with a custom error type
                    print("Error occurred when trying to open the file location.json")
                    return {"error": True, "type": "JSONFileError"}

            return {"error": False, "type": "NoDataFound"}
        except:
            # If the file could not be opened, it will return an error dictionary with a custom error type
            print("Error occurred when trying to open the file location.json")
            return {"error": True, "type": "JSONFileError"}
