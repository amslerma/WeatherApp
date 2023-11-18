import os
import tempfile
import requests
import json
import pandas as pd
import re
import numpy


# Extracts the long and lat number from the string.
def regexlonglat(coordinate):
    output = re.search("(\d+.\d+)", numpy.array_str(coordinate))
    output = output.group()
    return output


# Returns the longitude and latitude for the specified city
def get_coordinates(city_name):
    # Opens the list with cities as dataframe
    world_list = pd.read_csv("worldcities.csv")

    # Remove white spaces & lower case for case insensitive comparison
    city_name = city_name.strip().lower()

    # Extracts longitude and latitude for the requested city
    lng = world_list.loc[(world_list["city"].str.strip().str.lower() == city_name), ["lng"]].values
    lat = world_list.loc[(world_list["city"].str.strip().str.lower() == city_name), ["lat"]].values

    # extracts number since string contains brackets
    if lng.size > 0 and lat.size > 0:
        lng2 = regexlonglat(lng)
        lat2 = regexlonglat(lat)
        return lat2, lng2
    else:
        return


# User interaction
print("---- Weather App ----")
check = "y"
while check == "y":
    city = input("Type a city you want to know the weather of: (type \"n\" to exit)")
    if city != "n":
        try:
            latitude, longitude = get_coordinates(city)
            # Add functionality to call the weather api and return the weather.
            print(city)
            print(longitude)
            print(latitude)
        except:
            print("The city was not found. Try another city.")
    else:
        check = "n"
        print("Application closed")


# API call from open-meteo
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 47.3925,
        "longitude": 8.0442,
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain",
                    "showers", "snowfall", "weather_code", "wind_speed_10m"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "precipitation_sum",
                  "rain_sum", "showers_sum", "snowfall_sum", "precipitation_hours", "precipitation_probability_max",
                  "wind_speed_10m_max"],
        "timezone": "Europe/Berlin"
    }

    try:
        # `request` ist eine Python-Bibliothek, die HTTP-Anfragen vereinfacht (muss heruntergeladen werden)
        response = requests.get(url, params=params)
        response.raise_for_status()  # wirft eine Ausnahme, wenn der HTTP-Statuscode nicht erfolgreich ist

        weather_data = json.loads(response.text)

        # Der Pfad wird relativ zum aktuellen Arbeitsverzeichnis des Projekts angegeben
        temp_dir = os.path.join(os.getcwd(), "temp_directory")
        os.makedirs(temp_dir, exist_ok=True)  # Erstellt das Verzeichnis, falls es nicht existiert

        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_dir) as temp_file:
            json.dump(weather_data, temp_file)
            temp_file_path = temp_file.name
            print(f"Daten wurden in die temporäre Datei {temp_file_path} geschrieben.")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Senden der HTTP-Anfrage: {e}")
    except json.JSONDecodeError as e:
        print(f"Fehler beim Verarbeiten der JSON-Antwort: {e}")
    except Exception as e:
        print(f"Allgemeiner Fehler: {e}")


if __name__ == "__main__":
    get_weather()
