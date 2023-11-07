import os
import tempfile
import requests
import json


# Wetterdaten von der open-meteo API holen und speichern (verarbeiten)
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
