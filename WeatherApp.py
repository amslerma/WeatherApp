import os
import tempfile
import requests
import json
import pandas as pd
import re
import numpy
import warnings
from datetime import datetime
from numpy.core.defchararray import upper

temp_file_path = ''

weather_codes = {
    0: "Klarer Himmel",
    1: "Hauptsächlich klar",
    2: "Teilweise bewölkt",
    3: "Bedeckt",
    45: "Nebel und Rauhreif",
    48: "Nebel und Rauhreif",
    51: "Nieselregen: Leichte Intensität",
    53: "Nieselregen: Moderate Intensität",
    55: "Nieselregen: Starke Intensität",
    56: "Gefrierender Nieselregen: Leichte Intensität",
    57: "Gefrierender Nieselregen: Starke Intensität",
    61: "Regen: Leichte Intensität",
    63: "Regen: Moderate Intensität",
    65: "Regen: Starke Intensität",
    66: "Gefrierender Regen: Leichte Intensität",
    67: "Gefrierender Regen: Starke Intensität",
    71: "Schneefall: Leichte Intensität",
    73: "Schneefall: Moderate Intensität",
    75: "Schneefall: Starke Intensität",
    77: "Schneekörner",
    80: "Regenschauer: Leichte Intensität",
    81: "Regenschauer: Moderate Intensität",
    82: "Regenschauer: Starke Intensität",
    85: "Schneeschauer: Leichte Intensität",
    86: "Schneeschauer: Starke Intensität",
    95: "Gewitter: Geringe oder mässige Intensität",
    96: "Gewitter mit Hagel: Geringe Intensität",
    99: "Gewitter mit Hagel: Starke Intensität"
}

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


# API call from open-meteo
def get_weather(latiude, longitude):
    global temp_file_path
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
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

        # The path is specified relative to the current working directory of the project
        temp_dir = os.path.join(os.getcwd(), "temp_directory")
        os.makedirs(temp_dir, exist_ok=True)  # Creates the directory if it does not exist

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

def print_weather(temp_file_path, unit):
    try:
        # Open the file in read mode and load the content with json.loads()
        with open(temp_file_path, 'r') as file:
            # Deserialisiere das JSON
            wetterdaten = json.load(file)
            aktuelle_wetterdaten = wetterdaten["current"]
            date_time = datetime.fromisoformat(aktuelle_wetterdaten['time'])
            print("Aktuelle Wetterdaten:")
            print(f"Wettercode: {weather_codes.get(aktuelle_wetterdaten['weather_code'])}")
            print(f"Luftfeuchtigkeit: {aktuelle_wetterdaten['relative_humidity_2m']}%")

            # The weather data is output here with the EU units
            if unit == "EU":
                eu_time = date_time.strftime("%d.%m.%Y %H:%M")
                print("Zeit:", eu_time)
                print(f"Temperatur: {aktuelle_wetterdaten['temperature_2m']} °C")
                print(f"scheinbare Temperatur: {aktuelle_wetterdaten['apparent_temperature']} °C")
                print(f"Niederschlag: {aktuelle_wetterdaten['precipitation']} mm")
                print(f"Windgeschwindigkeit: {aktuelle_wetterdaten['wind_speed_10m']} km/h")

            # The weather data is output here with the US units
            else:
                print("Zeit: ", date_time)
                print("Temperatur:", (aktuelle_wetterdaten['temperature_2m'] * 1.8) + 32, "°F")
                print("Scheinbare Temperatur:", (aktuelle_wetterdaten['apparent_temperature'] * 1.8) + 32, "°F")
                print("Niederschlag:", (aktuelle_wetterdaten['precipitation'] / 25.4), "inches")
                print(f"Windgeschwindigkeit:", round((aktuelle_wetterdaten['wind_speed_10m'] / 1.60934), 2), "mph")


    except FileNotFoundError:
        print(f"Die Datei '{temp_file_path}' wurde nicht gefunden.")
    except json.JSONDecodeError as e:
        print(f"Fehler beim Deserialisieren des JSON: {e}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")


# User interaction
print("---- Weather App ----")
check = "y"

while check == "y":
    city = input("Type a city you want to know the weather of: (type \"n\" to exit)")
    unit = upper(input("Type the desired weather unit: US or EU"))
    if city != "n":
        if unit == "EU" or unit == "US":
            try:
                latitude, longitude = get_coordinates(city)
                # Add functionality to call the weather api and return the weather.
                print(city)
                get_weather(latitude, longitude)
                print_weather(temp_file_path, unit)
            except:
                print("The city was not found. Try another city.")
        else:
            print("The unit is not correct.")
    else:
        check = "n"
        print("Application closed")


if __name__ == "__main__":
    get_weather()




