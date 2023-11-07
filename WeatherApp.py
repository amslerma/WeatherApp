import os
import tempfile
import requests
import json

# get weather-data from open-meteo api and saves to temporary file
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 47.3925,
        "longitude": 8.0442,
        "current": "temperature_2m",
        "hourly": "temperature_2m",
        "daily": "weather_code",
        "timezone": "Europe/Berlin"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        weather_data = json.loads(response.text)

        # Der Pfad wird relativ zum aktuellen Arbeitsverzeichnis des Projekts angegeben
        temp_dir = os.path.join(os.getcwd(), "temp_directory")
        os.makedirs(temp_dir, exist_ok=True)  # Erstelle das Verzeichnis, falls es nicht existiert

        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=temp_dir) as temp_file:
            json.dump(weather_data, temp_file)
            temp_file_path = temp_file.name
            print(f"Daten wurden in die temporäre Datei {temp_file_path} geschrieben.")

    else:
        print(f"Fehler beim Abrufen der Wetterdaten. Statuscode: {response.status_code}")


if __name__ == "__main__":
    get_weather()
